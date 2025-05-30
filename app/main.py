"""
FastAPI 앱 실행 + 라우팅 연결
"""
from fastapi import FastAPI
from app.agent_graph import agent_app

app = FastAPI()
app.include_router(agent_app)
