"""테스트는 개발 데이터(public.members)를 건드리지 않고
테스트 전용 스키마(test_chapter13)에서만 실행한다."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db import Base, DATABASE_URL, get_db
from app.main import app
from app import models  # noqa: F401  (Base 에 Member 테이블을 등록)

TEST_SCHEMA = "test_chapter13"


@pytest.fixture(scope="session")
def test_engine():
    # 이 엔진은 search_path 가 테스트 스키마 하나뿐이라 public 테이블에는 닿지 않는다
    engine = create_engine(
        DATABASE_URL,
        connect_args={"options": f"-c search_path={TEST_SCHEMA}"},
    )
    with engine.begin() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
        conn.execute(text(f"CREATE SCHEMA {TEST_SCHEMA}"))
    Base.metadata.create_all(engine)  # 테스트 스키마 안에만 members 생성
    yield engine
    with engine.begin() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
    engine.dispose()


@pytest.fixture(scope="session")
def client(test_engine):
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
