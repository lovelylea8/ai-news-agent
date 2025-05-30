"""
벡터 기반 뉴스 유사도 검색 등 (예정)
"""
# app/retriever.py

# 추후: Pinecone 등 벡터DB로 뉴스 유사도 검색
def search_similar_news(keywords: list[str]):
    # 벡터 검색 기반 추천 로직 연결 예정
    return [f"'{kw}'와 유사한 뉴스 기사" for kw in keywords]
