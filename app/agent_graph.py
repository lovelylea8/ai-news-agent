"""
LangGraph 기반 FSM 구성 (상태 흐름)
"""
from fastapi import APIRouter
from langgraph.graph import StateGraph, END
from app.tools import extract_keywords, search_news, summarize_news

agent_app = APIRouter()

class State(dict):
    pass

builder = StateGraph(State)
builder.add_node("extract_keywords", extract_keywords)
builder.add_node("search_news", search_news)
builder.add_node("summarize_news", summarize_news)

builder.set_entry_point("extract_keywords")
builder.add_edge("extract_keywords", "search_news")
builder.add_edge("search_news", "summarize_news")
builder.add_edge("summarize_news", END)

graph = builder.compile()

@agent_app.post("/agent")
async def run_agent(query: str):
    state = {"query": query}
    result = graph.invoke(state)
    return {"summary": result["summary"]}
