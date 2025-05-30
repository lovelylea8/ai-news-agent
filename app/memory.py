"""
사용자 피드백 저장, 조회 등
"""
# app/memory.py

# 예시: 간단한 피드백 저장소
user_feedback_store = {}

def save_feedback(user_id: str, keyword: str, like: bool):
    user_data = user_feedback_store.setdefault(user_id, {})
    user_data[keyword] = user_data.get(keyword, 0) + (1 if like else -1)

def get_user_preferences(user_id: str):
    return user_feedback_store.get(user_id, {})
