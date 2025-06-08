import streamlit as st
import requests
import re

st.set_page_config(page_title="뉴스 추천 에이전트", layout="wide")
st.title("뉴스 요약 및 추천 에이전트")

query = st.text_input("관심 있는 주제를 입력하세요.", placeholder="예: 인공지능, 삼성전자, 주가, AI 트렌드 등")

def render_summary(summary: str):
    st.markdown("### GPT 요약 결과")

    with st.expander("AI 추천 뉴스 피드 펼쳐보기", expanded=True):
        # 1. <linkurl> → 마크다운 링크로 변환
        summary_md = re.sub(r"<linkurl>(.*?)</linkurl>", r"[링크 바로가기](\1)", summary)

        # 2. <linktext> → 질문 형식으로 변환
        summary_md = re.sub(r"<linktext>(.*?)</linktext>", r"\1", summary_md)

        # 3. <sourceid> 제거
        summary_md = re.sub(r"<sourceid>\d+</sourceid>", "", summary_md)

        # 4. 마크다운 렌더링
        st.markdown(summary_md.strip())

if st.button("뉴스 추천 받기") and query:
    with st.spinner("뉴스 분석 중..."):
        try:
            response = requests.post("http://localhost:8000/agent", json={"query": query})
            response.raise_for_status()

            payload = response.json()
            summary = payload.get("summary", "요약 결과 없음")
            news_list = payload.get("results", [])

            # GPT 요약 출력
            render_summary(summary)

            # 원본 뉴스 목록 출력
            if news_list:
                st.markdown("### 관련 뉴스 목록")
                for i, news in enumerate(news_list, 1):
                    title = news.get("title", "제목 없음")
                    link = news.get("originallink") or news.get("link")
                    if not link or not link.startswith("http"):
                        continue  # 유효하지 않은 링크는 건너뜀

                    description = news.get("description", "")
                    pub_date = news.get("pubDate", "날짜 미상")
                    doc_id = news.get("id", "")

                    st.markdown(f"**{i}. [{title}]({link})**")
                    st.markdown(f"- ID: {doc_id}")
                    st.markdown(f"- {pub_date}")
                    st.markdown(f"- {description[:100]}...")
                    st.markdown("---")
            else:
                st.warning("관련 뉴스를 찾지 못했어요.")
        except Exception as e:
            st.error(f"오류 발생: {e}")
