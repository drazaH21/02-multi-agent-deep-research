import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.graph import build_research_graph

load_dotenv()

def test_research_workflow():
    print("Initializing Multi-Agent Deep Research System...")
    
    if not os.getenv("GROQ_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        print("ERROR: GROQ_API_KEY or TAVILY_API_KEY is missing in your .env file!")
        return

    app = build_research_graph()

    initial_state = {
        "topic": "State of Agentic AI Workflows and LangGraph in Enterprise Architecture 2026",
        "sub_queries": [],
        "search_results": [],
        "critique_notes": "",
        "final_report": "",
        "iteration_count": 0
    }

    print(f"\nRunning research graph for topic: '{initial_state['topic']}'\n" + "="*50)
    
    final_state = app.invoke(initial_state)

    print("\n" + "="*50)
    print("FINAL SYNTHESIZED RESEARCH REPORT:")
    print("="*50)
    print(final_state.get("final_report"))

    # Save report locally for portfolio review
    report_filename = "research_report.md"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(final_state.get("final_report"))
    print(f"\nReport successfully saved to {report_filename}")

if __name__ == "__main__":
    test_research_workflow()
