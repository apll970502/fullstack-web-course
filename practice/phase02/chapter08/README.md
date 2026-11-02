# Chapter 08 — PUT/PATCH + UPDATE

## API Contract
| 메서드 | 요청 | 성공 | 실패 |
|---|---|---|---|
| `PUT /members/{id}` | name, email, age 전부 필수 | 200 + MemberResponse | 404 회원 없음 / 409 이메일 중복 / 422 입력 오류 |
| `PATCH /members/{id}` | 바꿀 필드만 (생략 허용, explicit null 금지) | 200 + MemberResponse | 400 빈 요청 / 404 / 409 / 422 (null 포함) |

- 생략 = 기존 값 유지, `"email": null` = 이번 Contract 에서는 422
- 이메일 중복 검사는 **자기 자신 제외** (`id <> %s`)
- SQL 값은 `%s` 파라미터, 컬럼명은 `allowed_fields` 허용 목록에서만 선택

## 실행 (phase02 의 .venv 사용)
```
python -m uvicorn main:app --reload
```

## 검증 결과 (member id 11 사용, 확인 후 원래 값으로 복구)
| 시험 | 결과 |
|---|---|
| PATCH `{"age": 26}` | 200, name/email 유지, GET 재조회 일치 |
| PATCH `{}` | 400 |
| PATCH `{"email": null}` | 422 |
| PATCH 없는 id | 404 |
| PATCH 다른 회원의 이메일 | 409 |
| PATCH 자기 자신의 이메일 | 200 (자기 제외 확인) |
| PUT 필드 누락 | 422 |
| PUT 없는 id | 404 |
| PUT 전체 수정 | 200 |

## 독립 실습 — PUT/PATCH /courses/{id}
- 중복 조건: 같은 title + instructor (자기 자신 제외) → 409
- PATCH 는 안 보낸 값을 기존 값으로 채워 최종 title+instructor 로 중복 검사

| 시험 | 결과 |
|---|---|
| PATCH capacity 변경 | 200, GET 재조회 일치 |
| PATCH `{}` | 400 |
| PATCH `{"title": null}` | 422 |
| PATCH capacity="abc" | 422 |
| PATCH 없는 id | 404 |
| PATCH 다른 강좌와 같은 title+instructor | 409 |
| PUT 필드 누락 | 422 |
| PUT 없는 id | 404 |
| PUT 전체 수정(원복) | 200 |

## Definition of Done
- [x] PUT/PATCH 차이 설명
- [x] PUT 이 실제 DB 행을 수정
- [x] PATCH 가 전달한 필드만 수정
- [x] PATCH `{"email": null}` 422, `{}` 400, 없는 id 404, 중복 이메일 409
- [x] Parameterized Query 사용
- [x] Swagger 로 PUT / PATCH / GET 재조회 확인 (404·409·`age:"abc"` 는 자동 시험으로 확인)
- [x] 독립 실습: PUT/PATCH /courses/{id}
- [x] Commit / Push
