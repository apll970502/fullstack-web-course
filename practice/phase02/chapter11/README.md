# Chapter 11 — SQLAlchemy ORM 기초 (Model / Table / Session)

기존 `members` 테이블을 **새로 만들지 않고** ORM Model 로 매핑해서 조회한다.

| SQL / psycopg | SQLAlchemy ORM |
|---|---|
| Table | `Member` 클래스 (`__tablename__ = "members"`) |
| Row | `Member` 객체 |
| SELECT ... WHERE | `select(Member).where(...)` |
| Connection | Engine / Session |
| COMMIT / ROLLBACK | `session.commit()` / `session.rollback()` |

## 구조
```
chapter11/app/
├─ db.py       Engine(echo=True), SessionLocal, Base  (접속 정보 = phase02/.env)
├─ models.py   Member  ← 실제 public.members 와 1:1 매핑
└─ main.py     전체 조회 / 단건 조회 / Raw SQL 비교 / 없는 회원
```

## 실행 (chapter11 폴더에서, phase02 의 .venv)
```
python -m app.main
```

## Model 과 실제 DB 대조 (information_schema 로 확인)
| 컬럼 | 실제 DB | Model |
|---|---|---|
| id | integer PK NOT NULL | `Integer, primary_key=True` |
| name | varchar(50) NOT NULL | `String(50), nullable=False` |
| email | varchar(100) UNIQUE NOT NULL | `String(100), nullable=False, unique=True` |
| age | integer **NULL 허용** | `Integer, nullable=True` |
| joined_at | date NULL 허용 | `Date, nullable=True` |

강의 글의 예시(`member_id`, `varchar(100/255)`, age NOT NULL)와 우리 테이블은 다르다.
**글이 아니라 실제 DB 를 기준으로** 매핑했다. `create_all()` 은 쓰지 않았다.

## Evidence
- 전체 조회: 10행 출력, SQL 로그 `SELECT members.id, ... FROM members ORDER BY members.id`
- id=11: ORM 객체 `(11, 테스트1, test1@example.com, 25)`
- 같은 조회를 Raw SQL 로 실행 → `Raw SQL == ORM Object: True`
- id=999999 → `None` (FastAPI 에서는 404 로 바꿀 값)

## Definition of Done
- [x] SQLAlchemy 설치 (2.1.7)
- [x] 환경변수 기반 Database URL (`URL.create`)
- [x] Member Model 이 실제 members 와 일치
- [x] 전체 / 특정 회원 ORM 조회 성공, 없는 회원 None
- [x] echo SQL 확인, Raw SQL 결과 = ORM 결과
- [x] .env 는 Git 제외 (phase02/.env)
- [ ] Session 흐름을 내 말로 설명
- [ ] Commit / Push
