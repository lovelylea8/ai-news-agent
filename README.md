# 백엔드 서버 실행
uvicorn app.agent_graph:agent_app --host 0.0.0.0 --port 8000

# UI 실행
streamlit run ui/ui_app.py
