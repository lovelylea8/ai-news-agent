import logging
import requests
from readability import Document
from bs4 import BeautifulSoup
from typing import Dict, Any
from openai import OpenAI

# OpenAI 클라이언트 초기화
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
    logging.info('▶▶▶ summarize_news() 실행')

    articles = state.get("news_results", [])
    query = state.get("query", "관련 주제")
    logging.info(f'전달된 뉴스 개수: {len(articles)}')

    news_blocks = []

    for i, article in enumerate(articles):
        doc_id = article.get("id", f"news-{i+1}")
        title = article.get("title", "제목 없음")
        url = article.get("originallink", "")
        pub_date = article.get("pubDate", "날짜 없음")
        content = extract_main_text_from_url(url) if url else "본문 없음"

        news_block = (
            f"ID: {doc_id}\n"
            f"제목: {title}\n"
            f"날짜: {pub_date}\n"
            f"본문: {content}\n"
            f"URL: {url}"
        )
        news_blocks.append(news_block)

    prompt = f"""당신은 사용자의 쿼리에 따라 관련 뉴스를 수집하고 분석한 요약 전문가입니다.

뉴스들을 분석한 후, 반드시 아래 형식에 따라 응답해주세요:

##### 1. 추천 뉴스
① 뉴스 원문: [뉴스 고유 ID]
 - 제목: [제목]
 - 요약: [1000자 이내]
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

---
다음은 '{query}'와 관련된 뉴스들입니다:

""" + "\n\n---\n\n".join(news_blocks)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 뉴스 요약 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        summary_text = response.choices[0].message.content.strip()
        state["summary"] = summary_text
    except Exception as e:
        logging.error(f"요약 실패: {e}")
        state["summary"] = "요약 중 오류가 발생했습니다."

    return state
