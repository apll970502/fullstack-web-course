"""SQLAlchemy Engine / Session. 접속 정보는 phase02/.env (common/db.py 와 같은 값)."""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

# f-string 대신 URL.create: 비밀번호에 특수문자가 있어도 안전하다.
DATABASE_URL = URL.create(
    "postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.environ["DB_NAME"],
)

# echo=True: ORM 코드 뒤에서 실제 실행되는 SQL 을 터미널에 출력 (학습용)
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"options": "-c search_path=practice,public"},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass
