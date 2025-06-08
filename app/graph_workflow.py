from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any, List
from app.extract_keyword import extract_keywords
from app.tools import search_news
from app.summarize import summarize_news
import logging

# 상태 스키마 정의
StateType = TypedDict('GraphState', {
    'query': str,
    'keywords': List[str],
    'news_results': List[Dict[str, Any]],
    'summary': str,
    'error': str
})

def check_keywords(state: StateType) -> str:
    if not state.get('keywords'):
        state['error'] = '키워드가 없습니다.'
        return END
    return 'search_news'


def create_workflow():
    # 워크플로우 객체 생성
    workflow = StateGraph(StateType)

    # 노드 등록
    workflow.add_node('extract_keywords', extract_keywords)
    workflow.add_node('search_news', search_news)
    workflow.add_node('summarize_news', summarize_news)

    # 흐름 설정
    workflow.set_entry_point('extract_keywords')
    workflow.add_conditional_edges(
        'extract_keywords',
        check_keywords,
        {'search_news': 'search_news', END: END}
    )
    workflow.add_edge('search_news', 'summarize_news')
    workflow.add_edge('summarize_news', END)

    return workflow.compile()
