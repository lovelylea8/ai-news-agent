import logging
from app.crawler import crawl_naver_news
from app.vector_search import store_news_to_pinecone, query_news_from_pinecone

def search_news(state):
    logging.info("▶▶▶ search_news() 실행")
    keywords = state.get("keywords", [])
    all_results = []

    for keyword in keywords:
        logging.info(f"▶ 키워드 검색 중: {keyword}")
        results = crawl_naver_news(keyword, 5)
        store_news_to_pinecone(results)  # 벡터 DB에 저장
        retrieved = query_news_from_pinecone(keyword, top_k=3)  # 벡터 DB에서 유사도 기반 검색
        all_results.extend(retrieved)

    state["news_results"] = all_results
    return state

### 초기 버전
# def search_news(state):
#     logging.info('▶▶▶ search_news() 실행')
#     keywords = state.get("keywords", [])
#     keyword_str = " ".join(keywords)
#
#     articles = crawl_naver_news(keyword_str, 10)
#     store_news_to_pinecone(articles)  
#     search_results = query_news_from_pinecone(keyword_str, top_k=3)  # 벡터 DB에서 유사도 기반 검색
#
#     state["news_results"] = search_results
#     return state


# def summarize_news(state):
#     logging.info('▶▶▶ summarize_news() 실행')
#     articles = state.get("news_results", [])
#     summary = "\n".join([
#         f"요약: {a['title']} - {a['content'][:50]}..." for a in articles
#     ])
#     state["summary"] = summary
#     return state
