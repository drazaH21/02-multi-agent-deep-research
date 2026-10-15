from langgraph.graph import StateGraph, END
from src.state import ResearchState
from src.agents import planner_node, research_node, critic_node, synthesizer_node

def build_research_graph():
    """
    Builds the LangGraph state graph linking Planner -> Researcher -> Critic -> Synthesizer.
    """
    workflow = StateGraph(ResearchState)

    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # Define graph edges / flow
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "critic")
    workflow.add_edge("critic", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()
