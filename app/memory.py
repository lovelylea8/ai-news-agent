# memory.py: 사용자 피드백을 SQLite로 저장하고 관리하며, 스레드 안전성을 보장
import sqlite3
from threading import Lock
from typing import Dict
import os

# 데이터베이스 연결과 테이블 초기화
def init_db():
    """SQLite 데이터베이스를 초기화하고 피드백 테이블을 생성"""
    conn = sqlite3.connect("user_feedback.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            user_id TEXT,
            keyword TEXT,
            score INTEGER,
            PRIMARY KEY (user_id, keyword)
        )
    """)
    conn.commit()
    return conn, cursor

# 전역 변수: 데이터베이스 연결과 락
conn, cursor = init_db()
lock = Lock()

def save_feedback(user_id: str, keyword: str, like: bool) -> None:
    """
    사용자 피드백을 저장. 좋아요(like=True)면 +1, 싫어요(like=False)면 -1.
    스레드 안전성을 위해 락 사용. 점수는 -10 ~ 10으로 제한.
    """
    score = 1 if like else -1
    with lock:
        cursor.execute("""
            INSERT INTO feedback (user_id, keyword, score)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, keyword) DO UPDATE
            SET score = MAX(MIN(score + ?, 10), -10)
        """, (user_id, keyword, score, score))
        conn.commit()

def get_user_preferences(user_id: str) -> Dict[str, int]:
    """
    사용자의 키워드별 피드백 점수를 조회.
    점수가 0보다 큰 키워드만 반환해 긍정적 선호도 강조.
    """
    with lock:
        cursor.execute("SELECT keyword, score FROM feedback WHERE user_id = ? AND score > 0", (user_id,))
        return dict(cursor.fetchall())

def close_db() -> None:
    """데이터베이스 연결 종료"""
    conn.close()

# 프로그램 종료 시 DB 연결 닫기
import atexit
atexit.register(close_db)