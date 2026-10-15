import os
import json
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv
from src.state import ResearchState

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def planner_node(state: ResearchState) -> ResearchState:
    """
    Planner agent that breaks down the main research topic into 3 distinct sub-queries.
    """
    topic = state["topic"]
    print(f"\n[Planner Agent] Deconstructing topic: '{topic}'...")

    prompt = (
        f"You are an expert research director. Break down the following research topic "
        f"into exactly 3 specific, highly effective search queries to gather comprehensive data.\n\n"
        f"Topic: {topic}\n\n"
        "Return ONLY a JSON object with a key 'sub_queries' containing an array of 3 strings."
    )

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    try:
        parsed = json.loads(content)
        sub_queries = parsed.get("sub_queries", [topic])
    except Exception:
        sub_queries = [topic]

    print(f"[Planner Agent] Generated sub-queries: {sub_queries}")
    return {**state, "sub_queries": sub_queries, "iteration_count": state.get("iteration_count", 0) + 1}


def research_node(state: ResearchState) -> ResearchState:
    """
    Research agent that executes Tavily web searches for each sub-query.
    """
    print(f"\n[Research Agent] Executing web searches via Tavily...")
    sub_queries = state.get("sub_queries", [state["topic"]])
    all_results = []

    for q in sub_queries:
        try:
            print(f"Searching: {q}")
            res = tavily_client.search(query=q, max_results=2)
            for r in res.get("results", []):
                all_results.append({
                    "query": q,
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "content": r.get("content")
                })
        except Exception as e:
            print(f"Search error for query '{q}': {e}")

    return {**state, "search_results": all_results}


def critic_node(state: ResearchState) -> ResearchState:
    """
    Critic agent that evaluates search results for gaps, credibility, or missing perspectives.
    """
    print(f"\n[Critic Agent] Evaluating gathered research findings for quality and gaps...")
    topic = state["topic"]
    results = state.get("search_results", [])

    summaries = "\n".join([f"- {r['title']}: {r['content'][:150]}..." for r in results])

    prompt = (
        f"You are a rigorous managing editor. Review the collected search snippets for the research topic: '{topic}'.\n\n"
        f"Collected Findings Snippets:\n{summaries}\n\n"
        "Identify any major technical gaps, missing enterprise angles, or areas needing deeper focus. "
        "Provide concise critique notes to guide the final synthesizer."
    )

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300
    )

    critique_notes = response.choices[0].message.content
    print(f"[Critic Agent] Critique notes generated successfully.")
    return {**state, "critique_notes": critique_notes}


def synthesizer_node(state: ResearchState) -> ResearchState:
    """
    Synthesizer agent that compiles research findings and critique notes into a structured Markdown report with citations.
    """
    print(f"\n[Synthesizer Agent] Synthesizing final research report incorporating critic feedback...")
    topic = state["topic"]
    results = state.get("search_results", [])
    critique = state.get("critique_notes", "None")

    formatted_sources = "\n".join(
        [f"- **[{r['title']}]({r['url']})**: {r['content']}" for r in results]
    )

    prompt = (
        f"You are a principal technical writer. Write a comprehensive, executive-level deep research report "
        f"on the topic: '{topic}' based strictly on the gathered web findings and editor critique notes.\n\n"
        f"Editor Critique Notes to Address:\n{critique}\n\n"
        f"Research Findings:\n{formatted_sources}\n\n"
        "Format the report professionally in Markdown with an Executive Summary, Key Findings, Technical Architecture Details, and Sources Cited."
    )

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500
    )

    final_report = response.choices[0].message.content
    print(f"[Synthesizer Agent] Upgraded report generated successfully.")
    return {**state, "final_report": final_report}
