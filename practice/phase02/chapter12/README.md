# Chapter 12 — SQLAlchemy ORM 기반 CRUD (Repository / Session / Commit / Rollback)

10강의 Router → Service → Repository 구조를 유지하고, Repository 구현만 SQL(psycopg)에서 ORM(SQLAlchemy)으로 바꿨다. API Contract 는 그대로다.

## 폴더 구조
```
chapter12/app/
├─ main.py                       앱 조립
├─ db.py                         Engine(echo=True), SessionLocal, Base, get_db()
├─ models.py                     Member  ← public.members (member_id, name, email, age)
├─ schemas.py                    MemberCreate / Update / Patch / Response
├─ routers/member_router.py      HTTP (Depends(get_db))
├─ services/member_service.py    404 / 409 / 400 판단, IntegrityError -> 409
└─ repositories/member_repository.py   ORM CRUD + commit / rollback
```
접속 정보는 `phase02/.env` (chapter 공통).

## 실행 (chapter12 폴더에서)
```
python -m uvicorn app.main:app --reload
```

## SQL CRUD ↔ ORM CRUD
| 동작 | ORM 코드 | 로그에서 보이는 SQL |
|---|---|---|
| Create | `Member(...)` + `add` + `commit` + `refresh` | INSERT + COMMIT |
| Read | `select()` / `db.get()` | SELECT |
| Update | 객체 속성 변경 + `commit` | UPDATE + COMMIT |
| Delete | `db.delete()` + `commit` | DELETE + COMMIT |
| 실패 | `rollback()` | ROLLBACK |

## Transaction 경계
이 장은 교육용 단순화로 **Repository 함수가 commit / rollback 을 수행**한다.
하나의 Service 작업이 여러 Repository 를 묶어야 하면 Service / Unit of Work 에서 경계를 잡는 것이 맞다.
(commit 을 어느 파일에 둘까 보다, 어디까지를 한 번의 성공/실패 단위로 볼까가 핵심)

## 오류 처리 (두 겹 방어)
- 1차: Service 가 `find_by_email` 로 미리 조회 → 중복이면 409
- 최종: DB UNIQUE 제약 위반(`IntegrityError`)을 Service 가 409 로 번역
- PUT / PATCH 는 사전 조회 없이 `IntegrityError` 번역만으로 409 를 낸다.

## 검증 결과 (임시 회원 생성 → 시험 → 삭제, 원래 5명 데이터 불변)
| 시험 | 결과 |
|---|---|
| GET 목록 / 단건 / 없는 id | 200 (5명) / 200 / 404 |
| POST 정상 / 중복 / 형식 오류 | 201 (member_id 포함) / 409 / 422 |
| PUT 정상 / 없는 id / 필드 누락 | 200 / 404 / 422 |
| PUT 다른 회원 이메일 (IntegrityError) | 409 |
| PATCH `{"age": 22}` | 200, age 만 변경 |
| PATCH `{}` / `{"email": null}` / 없는 id | 400 / 422 / 404 |
| PATCH 다른 회원 이메일 | 409 |
| DELETE / 재조회 / 재삭제 | 204 / 404 / 404 |
| 시험 후 목록 | 시험 전과 동일 |

SQLAlchemy Log: INSERT 1, UPDATE 4 (성공 2 + 실패 2), DELETE 1, COMMIT 4, ROLLBACK 확인.

## Definition of Done
- [x] GET 목록/상세 ORM 조회
- [x] POST 201, PUT/PATCH 200, DELETE 204
- [x] PATCH 생략/null 정책 유지 (`{}` 400, null 422)
- [x] 없는 회원 404, 중복 이메일 409
- [x] 실패 Transaction rollback 실행 (로그 확인)
- [x] Transaction 경계 위치 설명 (위 절)
- [x] SQLAlchemy Log 에서 의도한 SQL 확인
- [x] 기존 API Contract 유지
- [x] Swagger 화면에서 직접 확인 (GET 목록 / POST 201·409 / PATCH 200 / DELETE 204 / 재조회 5명; PUT·400·404·422 는 자동 시험으로 확인)
- [ ] Commit / Push
