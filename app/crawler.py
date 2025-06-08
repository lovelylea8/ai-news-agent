import os
import logging
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from readability import Document

import logging

# TODO: 로거 설정
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # DEBUG 레벨로 전체 로그 출력
# handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# 환경 변수 로드 (.env 파일에서 NAVER API 키 불러오기)
load_dotenv()

def crawl_naver_news(keyword: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    네이버 뉴스 검색 API를 사용해 뉴스 데이터 수집
    - 중복 URL 제거
    - title, description, originallink, link, pubDate 포함
    """
    headers = {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET")
    }

    if not headers["X-Naver-Client-Id"] or not headers["X-Naver-Client-Secret"]:
        raise ValueError("NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET이 설정되지 않았습니다.")

    url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&display={num_results}&sort=date"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 전체 응답 로그 찍기
        logging.debug(f"네이버 응답: {response.text}")

        # 응답에서 실제 뉴스 리스트 추출
        items = response.json().get("items", [])
        seen_urls = set()
        news_data = []

        for item in items:
            url = item.get("link")
            if url in seen_urls:
                continue  # 중복 제거
            seen_urls.add(url)

            news_data.append({
                "title": item.get("title", "").strip(),
                "description": item.get("description", "").strip(),
                "originallink": item.get("originallink", "").strip(),
                "link": url,
                "pubDate": item.get("pubDate", "").strip()
            })
            
        logging.info(f"키워드 '{keyword}'로 {len(news_data)}개 뉴스 크롤링 완료")
        return news_data

    except Exception as e:
        logging.error(f"뉴스 크롤링 실패: {e}")
        return []

def extract_main_text_from_url(url: str) -> str:
    resp = requests.get(url, timeout=5)
    doc = Document(resp.text)
    html = doc.summary()
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)