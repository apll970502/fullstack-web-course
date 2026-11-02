"""phase02 공통 DB 연결 모듈.

접속 정보는 practice/phase02/.env 에서 읽습니다. (.env 는 Git에 올리지 않습니다.)
사용법:
    from common.db import get_connection
"""
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# 어느 chapter 폴더에서 실행해도 phase02/.env 를 찾도록 절대경로로 지정
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_connection() -> psycopg.Connection:
    """호출할 때마다 새 연결을 반환합니다. 사용 후 close() 는 호출한 쪽 책임입니다."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        # members 등 테이블이 practice 스키마에 있어 SQL 에서 스키마명을 생략할 수 있게 함
        options="-c search_path=practice,public",
    )


if __name__ == "__main__":
    # python -m common.db  (phase02 폴더에서 실행) 로 연결 확인
    with get_connection() as conn:
        print("연결 성공:", conn.execute("SELECT version()").fetchone()[0])
