from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.graph_workflow import create_workflow
from typing import Dict, List, Any
import logging

agent_app = FastAPI()

class QueryInput(BaseModel):
    query: str  # 사용자 입력 쿼리
    
# 그래프 워크플로우 생성
graph = create_workflow()

# 메인 엔드포인트
@agent_app.post("/agent")
async def run_agent(input: QueryInput) -> Dict[str, Any]:
    """사용자 쿼리로 워크플로우 실행, 결과 반환"""
    logging.info(f"받은 쿼리: '{input.query}'")
    try:
        # 상태 초기화: 워크플로우에서 사용할 데이터 컨텍스트
        state = {
            "query": input.query,        # 입력 쿼리
            "keywords": [],              # 추출된 키워드
            "news_results": [],          # Pinecon 벡터 기반 뉴스 검색 결과
            "summary": "",               # GPT 요약 결과
            "error": ""                  # 오류 메시지
        }

        # 비동기 워크플로우 실행
        result = await graph.ainvoke(state)

        # HTTP 예외 처리
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])

        # 성공 시, 응답 반환
        return {
            "results": result.get("news_results", []),    # 뉴스 결과
            "summary": result.get("summary", "요약 실패"),  # 요약 결과
            "keywords": result.get("keywords", [])        # 키워드
        }

    except Exception as e:
        logging.exception("에이전트 실행 중 오류 발생")
        raise HTTPException(status_code=500, detail="서버 내부 오류")