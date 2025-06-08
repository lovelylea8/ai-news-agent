import logging
from app.crawler import crawl_naver_news
from app.vector_search import store_news_to_pinecone, query_news_from_pinecone

def extract_keywords(state):
    logging.info('▶▶▶ extract_keywords() 실행')
    query = state["query"]
    keywords = [kw.strip() for kw in query.lower().split() if len(kw) > 1]
    state["keywords"] = keywords
    return state

def search_news(state):
    logging.info('▶▶▶ search_news() 실행')
    keywords = state.get("keywords", [])
    keyword_str = " ".join(keywords)

    articles = crawl_naver_news(keyword_str, 5)
    store_news_to_pinecone(articles)  # 벡터 DB에 저장
    search_results = query_news_from_pinecone(keyword_str, top_k=3)  # 벡터 DB에서 유사도 기반 검색

    state["news_results"] = search_results
    return state

# def summarize_news(state):
#     logging.info('▶▶▶ summarize_news() 실행')
#     articles = state.get("news_results", [])
#     summary = "\n".join([
#         f"요약: {a['title']} - {a['content'][:50]}..." for a in articles
#     ])
#     state["summary"] = summary
#     return state
