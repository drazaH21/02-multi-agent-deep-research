from typing import List, TypedDict

class ResearchState(TypedDict):
    topic: str
    sub_queries: List[str]
    search_results: List[dict]
    critique_notes: str
    final_report: str
    iteration_count: int
