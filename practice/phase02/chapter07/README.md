# Chapter 07 — POST /members + INSERT + Transaction

## API Contract
- `POST /members` → 201 + `{id, name, email, age}`
- 형식 오류 → 422 / 이메일 중복 → 409 / DB 오류 → rollback 후 500
- `GET /members/{member_id}` → 200 / 없으면 404 (저장 검증용)

## 실행 (phase02 의 .venv 사용)
```
python -m uvicorn main:app --reload
```
DB 접속 정보는 `phase02/.env`, 연결 함수는 `phase02/common/db.py`.

## 검증 체크
- [ ] POST 201 + id
- [ ] DB SELECT 로 같은 row 확인
- [ ] GET /members/{id} 로 재조회
- [ ] 같은 이메일 재요청 → 409, row 수 불변
- [ ] email=not-email → 422
- [ ] SQL 컬럼명 일부러 틀림 → 500, row 없음 (확인 후 복구)

## 혼자 해보기 — POST /courses
- 테이블: `public.courses (id, title, instructor, capacity)`, UNIQUE(title, instructor)
- 중복 조건: 같은 title + instructor → 409

| 시험 | 결과 |
|---|---|
| 정상 POST | 201, id 1 저장 (DB count 0 → 1) |
| GET /courses/1 | 200, 저장값 일치 |
| 같은 강좌 재요청 | 409, count 불변 |
| capacity=0 | 422 (loc: body.capacity), count 불변 |
| INSERT 컬럼명 오류 | 500, count 불변 (rollback), 확인 후 복구 |

## Definition of Done
- [x] POST /members 201 + id
- [x] 실제 DB에 같은 row 존재
- [x] GET /members/{id} 재조회
- [x] 중복 409 / 잘못된 입력 422
- [x] DB 오류 500 + 데이터 미저장
- [x] commit = 성공한 변경 확정, rollback = 오류 난 Transaction 취소
- [x] .env 는 .gitignore 로 제외
- [ ] Commit / Push
