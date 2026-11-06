import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import member_router

# 실행 기록 형식: 언제 / 어떤 Level / 어느 모듈에서 / 무슨 일
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
# db.py 의 echo=True 대신 logging 으로 SQL 을 한 줄 형식으로 남긴다 (중복 출력 방지)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

app = FastAPI(title="Chapter 14 - CORS / Frontend")

# 누가 호출해도 되는가? = allow_origins (Frontend 의 scheme + host + port 와 정확히 일치해야 함)
allowed_origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(member_router.router)
