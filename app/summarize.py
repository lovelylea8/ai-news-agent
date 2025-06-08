import os
import logging
import requests
from readability import Document
from bs4 import BeautifulSoup
from typing import Dict, Any
from openai import OpenAI

client = OpenAI()

def extract_main_text_from_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        doc = Document(response.text)
        html = doc.summary()
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        logging.error(f"본문 추출 실패: {e}")
        return ""

def summarize_news(state: Dict[str, Any]) -> Dict[str, Any]:
    logging.info('▶️ summarize_news() 실행')

    articles = state.get("news_results", [])
    keyword = state.get("query", "관련 주제")
    logging.info(f'📄 전달된 뉴스 개수: {len(articles)}')

    news_blocks = []

    for i, article in enumerate(articles):
        doc_id = article.get("id", f"news-{i+1}")
        title = article.get("title", "제목 없음")
        url = article.get("originallink") or article.get("url") or article.get("link")
        date = article.get("pubDate", "날짜 미상")

        try:
            full_text = extract_main_text_from_url(url)
            if not full_text:
                raise ValueError("본문이 비어 있음")

            news_blocks.append(
                f"[{i+1}] ID: {doc_id}\n제목: {title}\n{full_text.strip()}\n"
            )
        except Exception as e:
            logging.error(f"본문 추출 실패 [{i+1}]: {e}")

    combined_news_text = "\n\n".join(news_blocks)

    prompt = f"""
다음은 '{keyword}' 키워드로 검색한 뉴스 결과입니다. 각 뉴스에는 고유 ID가 포함되어 있습니다.

{combined_news_text}

뉴스들을 분석한 후, 반드시 아래 형식에 따라 응답해주세요:

##### 1. 추천 뉴스
① 뉴스 원문: [뉴스 고유 ID]
 - 제목: [제목]
 - 요약: [100자 이내]
 - 날짜: [날짜]
 - 추천 이유: [뉴스 내용을 바탕으로 간단히 설명]
<linkurl>[원본 URL]</linkurl>

② (있다면 동일한 형식으로)
③ (있다면 동일한 형식으로)
④ (있다면 동일한 형식으로)
⑤ (있다면 동일한 형식으로)

##### 2. 맞춤 인사이트
 - 인사이트: [뉴스 데이터를 바탕으로 작성]
 - 적용 방안: [뉴스 데이터를 바탕으로 작성]

##### 3. 후속 질문 제안
 - 질문 1: <linktext>[뉴스 데이터와 관련된 질문]</linktext>
 - 질문 2: <linktext>[뉴스 데이터와 관련된 질문]</linktext>
 - 질문 3: <linktext>[뉴스 데이터와 관련된 질문]</linktext>
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 사용자가 원하는 뉴스를 친절하게 요약하고 추천해주는 개인 비서야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        final_summary = response.choices[0].message.content.strip()
        state["summary"] = final_summary
        logging.info("✅ GPT 요약 성공")
    except Exception as e:
        logging.error(f"GPT 요약 실패: {e}")
        state["summary"] = "요약 생성 실패: GPT 호출 중 오류 발생"

    return state
