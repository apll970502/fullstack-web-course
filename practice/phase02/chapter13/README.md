# Chapter 13 — 예외 처리 · Logging · TestClient

chapter12 의 ORM CRUD 코드를 그대로 복사해서 **예외 구분, Logging, 자동 테스트(pytest + TestClient)** 를 추가했다. API Contract 는 바뀌지 않는다.

## 오류의 의미 (Status 구분)
| Status | 의미 | Member API 예 |
|---|---|---|
| 400 | 요청 의미 자체가 부적절 | 빈 PATCH `{}` |
| 404 | 자원 없음 | 없는 member_id |
| 409 | 현재 데이터와 충돌 | 중복 email |
| 422 | Schema 검증 실패 | 잘못된 email/age |
| 500 | 예상 못한 서버 오류 | 예상 못한 DB/코드 오류 |

- 예외를 잡아서 `200 + {"success": false}` 로 돌려주지 않는다. HTTP Status 로 실패를 표현한다.

## Logging 규칙 (이 장에서 적용한 것)
| Level | 쓰는 곳 | 예 |
|---|---|---|
| INFO | 정상 주요 흐름 | `member created: member_id=9` |
| WARNING | 처리 가능한 비정상 (404/409/400) | `member not found: member_id=999999` |
| ERROR (`logger.exception`) | 예상 못한 오류 + Stack Trace | `unexpected error while creating member` |

- 형식: `시각 Level 모듈 메시지` (`logging.basicConfig`, `main.py`)
- Repository 는 DB 제약 위반(`IntegrityError`)은 WARNING, 그 밖의 오류는 `logger.exception` 으로 Stack Trace 까지 남기고 rollback 후 다시 raise 한다.
- 비밀정보는 남기지 않는다. PATCH 는 값 대신 **바뀐 필드 이름**만 기록한다 (`fields=['age']`). DB 비밀번호는 어디에도 출력하지 않는다.
- SQL 로그는 `echo=True` 대신 `logging.getLogger("sqlalchemy.engine")` 로 같은 형식에 합쳤다 (중복 출력 방지).

## 실행 (chapter13 폴더에서)
```
python -m uvicorn app.main:app --reload
```

## 검증 결과
| 시험 | Status | 남은 로그 |
|---|---|---|
| POST 정상 | 201 | INFO member created |
| GET 단건 / 없는 id | 200 / 404 | INFO lookup started / WARNING member not found |
| POST 중복 email | 409 | WARNING duplicate email |
| PATCH `{"age": 21}` | 200 | INFO member patched fields=['age'] |
| PATCH `{}` | 400 | WARNING empty patch request |
| PUT 다른 회원 email (DB 제약) | 409 | WARNING integrity error + duplicate email on update |
| DELETE | 204 | INFO member deleted |
| 예상 못한 DB 오류 (age=10^12 로 유도) | 예외 전파 | ERROR + Stack Trace, rollback 후 DB 에 행 없음 |

- 시험 후 members 는 시험 전과 같은 5명. 같은 로그 줄이 두 번 찍히는 중복은 0건.

## 자동 테스트 (pytest + TestClient)
```
chapter13/
├─ pytest.ini                 pythonpath = . / testpaths = tests
└─ tests/
   ├─ conftest.py             테스트 전용 스키마 생성/삭제, get_db 교체, TestClient
   └─ test_members.py         15개 테스트
```
실행 (chapter13 폴더에서): `python -m pytest -q`

**테스트 데이터 보호 (개발 DB ≠ 테스트 DB)**
- 세션 시작 때 `test_chapter13` 스키마를 만들고 그 안에만 `members` 를 만든다. 끝나면 스키마를 통째로 지운다.
- 테스트용 엔진의 `search_path` 는 테스트 스키마 하나뿐이라 `public.members` 에는 닿지 않는다.
- 앱의 `get_db` 를 `dependency_overrides` 로 테스트 세션으로 바꿔 끼운다.
- 이메일은 `uuid4` 로 매번 새로 만들어 재실행해도 충돌하지 않는다.

| 테스트 | 검증 계약 |
|---|---|
| GET 목록 / 단건 | 200 |
| GET 없는 id / 잘못된 id 타입 | 404 `Member not found` / 422 |
| POST 정상 / 중복 / 형식 오류 | 201 / 409 / 422 |
| PUT 정상 / 없는 회원 | 200 / 404 |
| PATCH 부분 수정 / 빈 body / null / 없는 회원 | 200(다른 필드 유지) / 400 / 422 / 404 |
| DELETE 정상 / 없는 회원 | 204 + 재조회 404 / 404 |

- 결과: **15 passed** (2회 연속 실행 모두 통과). 실행 전후 `public.members` 는 5행으로 동일하고 `test_chapter13` 스키마는 남지 않는다.
- 패키지: `pytest`, `httpx2` (현재 Starlette 의 TestClient 가 `httpx` 가 아니라 `httpx2` 를 요구)

## Definition of Done
- [x] 400 / 404 / 409 / 422 / 500 을 구분
- [x] HTTPException 으로 API 오류 표현
- [x] logging 으로 요청 흐름과 실패 위치 추적 (INFO / WARNING / exception)
- [x] 로그에 비밀정보 미출력
- [x] TestClient 로 Endpoint 호출, Status Code 와 Response JSON assert
- [x] 404 / 409 / 422 실패 Case 테스트
- [x] 테스트 데이터가 재실행을 방해하지 않음 (전용 스키마)
- [x] pytest 전체 실행 결과 확인 (15 passed)
- [ ] 코드 변경 뒤 Regression Test 재실행 (수정할 때마다 `pytest -q`)
- [ ] Commit / Push
