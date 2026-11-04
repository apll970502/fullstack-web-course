# Chapter 10 — Backend 구조화 (Router / Service / Repository / Schema / DB)

같은 API 동작을 유지하면서 책임만 나눈다.

```
Router (HTTP) → Service (업무 규칙) → Repository (SQL) → DB
Schema = Request/Response 계약, db.py = 연결 (phase02/common/db.py 재사용)
```

## 폴더 구조
```
chapter10/app/
├─ main.py                      앱 조립만
├─ db.py                        common.db.get_connection 재사용
├─ schemas.py                   MemberCreate / Update / Patch / Response
├─ routers/members.py           URL, Method, Status Code
├─ services/member_service.py   404 / 409 / 400 판단
└─ repositories/member_repository.py   SQL (HTTPException 없음)
```

## 실행 (chapter10 폴더에서)
```
python -m uvicorn app.main:app --reload
```
주의: `--reload` 는 chapter10 만 감시한다. `common/db.py` 를 고치면 서버를 다시 켠다.

## 책임 분리 확인
- Router / Service 에 `execute` (SQL) 없음
- Repository 에 `HTTPException` 없음
- 의존 방향: Router → Service → Repository → DB (역방향 import 없음)
- 연결 정보는 `phase02/.env` 한 곳

## Regression Test (임시 회원 생성 → 시험 → 삭제, 11번 회원 불변)
| 시험 | 결과 |
|---|---|
| POST 정상 / 중복 / 형식 오류 | 201 / 409 / 422 |
| GET 목록 / 단건 / 없는 id | 200 / 200 / 404 |
| PUT 정상 / 없는 id / 필드 누락 | 200 / 404 / 422 |
| PATCH 정상 / `{}` / null / 없는 id | 200 / 400 / 422 / 404 |
| PATCH 다른 회원 이메일 / 자기 이메일 | 409 / 200 |
| DELETE 정상 / 재조회 / 재삭제 | 204 / 404 / 404 |

## 참고
- 강의 글은 컬럼이 `member_id` 이지만 우리 테이블은 `id` 라서 `id` 로 유지했다 (기존 Response 계약 유지).
- 9강(DELETE)은 별도 폴더가 없어 이 장에서 함께 구현했다 (204, 없는 id 404).

## Definition of Done
- [x] Router / Service / Repository / Schema / DB 분리
- [x] Router 에 SQL 없음, Repository 에 HTTP 처리 없음
- [x] GET/POST/PUT/PATCH/DELETE Contract 유지
- [x] 자동 Regression Test 통과, import/runtime error 없음
- [x] .env Git 제외
- [ ] Swagger 에서 직접 Regression Test
- [ ] Commit / Push
