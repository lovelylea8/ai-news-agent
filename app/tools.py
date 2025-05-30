"""
벡터 기반 뉴스 유사도 검색 등 (예정)

"""
# app/tools.py
def extract_keywords(state):
    query = state["query"]
    keywords = [kw.strip() for kw in query.lower().split() if len(kw) > 2]
    state["keywords"] = keywords
    return state

def search_news(state):
    keywords = state.get("keywords", [])
    state["news_results"] = [f"{kw} 관련 뉴스 기사" for kw in keywords]
    return state

def summarize_news(state):
    articles = state.get("news_results", [])
    summary = "\n".join([f"요약: {a}" for a in articles])
    state["summary"] = summary
    return state
