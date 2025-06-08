import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

# 환경변수 불러오기 (.env 파일에 API KEY 저장)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_region = os.getenv("PINECONE_REGION", "us-east-1")

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=openai_api_key)

# Pinecone 클라이언트 초기화
pc = Pinecone(api_key=pinecone_api_key)
index_name = "news-index"

# 인덱스가 없다면 생성
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=pinecone_region)
    )
    logging.info(f"'{index_name}' 인덱스 생성 완료.")
else:
    logging.info(f"'{index_name}' 인덱스가 이미 존재합니다.")

# Pinecone 인덱스 객체 생성
index = pc.Index(index_name)


def store_news_to_pinecone(news_items: List[Dict[str, Any]]):
    """뉴스 데이터를 벡터화하고 Pinecone에 저장"""
    vectors = []
    for item in news_items:
        content = f"{item['title']} {item['description']}"  # 임베딩 입력 텍스트

        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=content
        )
        embedding = embedding_response.data[0].embedding

        # 모든 필드 포함한 메타데이터 저장
        vectors.append({
            "id": item["link"],  # 고유 ID
            "values": embedding,
            "metadata": {
                "title": item["title"],
                "description": item["description"],
                "link": item["link"],
                "originallink": item["originallink"],
                "pubDate": item["pubDate"]
            }
        })

    index.upsert(vectors=vectors)
    logging.info("뉴스 데이터를 Pinecone에 저장했습니다.")


def query_news_from_pinecone(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    print("[DEBUG] query_news_from_pinecone 함수 호출됨")
    print(f"[DEBUG] 입력 쿼리: {query}")
    
    try:
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        print("[DEBUG] 임베딩 생성 완료")
        
        query_vector = embedding_response.data[0].embedding
        search_response = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        print("[DEBUG] Pinecone 검색 완료")

        results = []
        for match in search_response.matches:
            if isinstance(match, dict):
                metadata = match.get("metadata", {})
                doc_id = match.get("id", "unknown")
            else:
                metadata = match.metadata
                doc_id = match.id
                
            results.append({
                "id": doc_id,
                **metadata
            })

        print("[DEBUG] 최종 결과:", results)
        return results

    except Exception as e:
        print(f"[ERROR] 예외 발생: {e}")
        return []

