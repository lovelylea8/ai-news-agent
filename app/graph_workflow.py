from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any, List
from app.tools import extract_keywords, search_news
from app.summarize import summarize_news
import logging

# 상태 스키마 정의
class GraphState(TypedDict):
    query: str
    keywords: List[str]
    news_results: List[Dict[str, Any]]
    summary: str
    error: str  # 에러 메시지 저장용

def create_workflow():
    """키워드 추출, 뉴스 검색, 요약 워크플로우 정의. 에러 처리와 조건부 분기 포함"""
    workflow = StateGraph(GraphState)

    # 노드 추가
    workflow.add_node("extract_keywords", extract_keywords)
    workflow.add_node("search_news", search_news)
    workflow.add_node("summarize_news", summarize_news)

    # 조건부 분기: 키워드가 없으면 요약 생략
    def check_keywords(state: Dict[str, Any]) -> str:
        if not state.get("keywords", []):
            state["error"] = "키워드를 추출하지 못했습니다."
            logging.warning(state["error"])
            return "end"
        return "search_news"

    # 워크플로우 흐름 정의
    workflow.set_entry_point("extract_keywords")
    workflow.add_conditional_edges(
        "extract_keywords",
        check_keywords,
        {"search_news": "search_news", "end": END}
    )
    workflow.add_edge("search_news", "summarize_news")
    workflow.add_edge("summarize_news", END)

    return workflow.compile()
