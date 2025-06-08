import json
import logging
from openai import OpenAI
from typing import Dict, Any

# OpenAI 클라이언트 초기화
client = OpenAI()

def extract_keywords(
    state: Dict[str, Any],
    model: str = "gpt-4",
    temperature: float = 0.1
) -> Dict[str, Any]:
    """
    사용자의 쿼리로부터 웹 검색에 최적화된 키워드를 GPT를 이용해 추출
    """
    logging.info('▶▶▶ extract_keywords() 실행')
    query = state.get("query", "")

    prompt = (
        f"사용자가 '{query}'라고 물어봤을 때, "
        "웹 검색에 최적화된 키워드 문구 3~5개를 가장 적절한 순위로 순차정렬하여 JSON 배열 형태로 출력해주세요."
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "당신은 검색 키워드 추출 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        text = resp.choices[0].message.content.strip()

        try:
            keywords = json.loads(text)
        except Exception as e:
            logging.warning(f"JSON 파싱 실패, 줄 단위 파싱 시도: {e}")
            keywords = [line.strip(' -') for line in text.splitlines() if line.strip()]

        logging.info(f"추출된 키워드: {keywords}")
        # 키워드를 3개로 제한
        state['keywords'] = keywords[:3]  # 처음 3개만 선택
    except Exception as e:
        logging.error(f"키워드 추출 실패: {e}")
        state['keywords'] = []

    return state