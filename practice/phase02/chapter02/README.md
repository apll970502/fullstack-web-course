# Phase 02 Chapter 02 학습 기록

## Path Parameter를 사용한 API

특정 자원 한 개를 가리킬 때 사용한다. 주소의 `{ }` 값이 함수 인자로 연결된다.

| API | 설명 |
|---|---|
| `GET /members/{member_id}` | 회원 번호로 회원 1명 조회 |
| `GET /courses/{course_id}` | 강좌 번호로 강좌 1개 조회 |

```
/members/3  →  member_id = 3  →  get_member(member_id=3)
```

- `member_id: int`로 타입을 정해 두면 FastAPI가 함수 실행 전에 정수인지 검사한다.
- 해당 번호가 없으면 `HTTPException(status_code=404)`를 일으킨다.

## Query Parameter를 사용한 API

목록에서 조건에 맞는 것만 걸러낼 때 사용한다. 주소의 `?` 뒤에 `이름=값`으로 붙인다.

| API | Query Parameter |
|---|---|
| `GET /members/search/` | `name` (선택) |
| `GET /members/filter/` | `name`, `min_age` (모두 선택) |
| `GET /courses/filter/` | `title`, `level` (모두 선택) |

- `name: str | None = None`은 "없어도 되는 선택 값"이라는 뜻이다.
- 여러 개는 `&`로 잇고, 순서가 바뀌어도 이름이 같으면 같은 결과가 나온다.
  (`?name=k&min_age=20` = `?min_age=20&name=k`)

## 두 방식을 구분한 기준

| 질문 | 방식 | 예 |
|---|---|---|
| 누구 하나를 정확히 가리키는가? | Path Parameter | `/members/3` |
| 목록을 조건으로 좁히는가? | Query Parameter | `/members/filter/?min_age=20` |

- 특정 번호가 없으면 → `404` (그런 자원이 없다)
- 검색 결과가 0건이면 → `200` + `[]` (요청은 정상, 결과만 비어 있다)
- 검색 조건을 모두 경로에 넣는 `/members/name/kim/min-age/20` 같은 방식은 확장성이 떨어진다.

## Swagger에서 확인한 200 / 404 / 422

| Case | 요청 | Code | 응답 |
|---|---|---|---|
| 정상 | `/members/1` | 200 | Kim 회원 객체 1개 |
| 없는 회원 | `/members/99` | 404 | `{"detail":"Member not found"}` |
| 잘못된 타입 | `/members/abc` | 422 | `type: int_parsing`, `loc: ["path","member_id"]` |
| 강좌 필터 | `/courses/filter/?level=2` | 200 | Frontend, FastAPI |

- 404와 422의 차이: 404는 "형식은 맞는데 그런 자원이 없다", 422는 "형식부터 틀렸다".
- 422의 `loc`에 `path`가 나오면 Path Parameter 문제, `query`가 나오면 Query Parameter 문제다.
- 422는 내가 만든 함수가 실행되기 전에 FastAPI가 `int` 타입 선언만 보고 먼저 걸러낸다.
- Swagger의 Responses 안내표에는 `200`, `422`만 나오고 `404`는 없다.
  `HTTPException`은 문서에 자동으로 표시되지 않기 때문이며, 실제로는 `404`가 나온다.

## 발생한 오류와 해결 과정

- `/members/search?name=kim`(끝에 `/` 없음)을 요청하면 `422`가 난다.
  `search`가 `{member_id}` 자리로 해석되어 `int` 검사에 실패하기 때문이다.
  글의 방식은 끝의 `/`에 따라 결과가 달라져 헷갈리기 쉽다.
  `/members?name=kim`처럼 목록 경로 하나에 Query Parameter를 붙이는 방식이 더 안전하다고 판단했다.
- `name=k`로 검색하면 `Park`도 나온다. `in` 연산이라 이름 중간에 `k`가 있어도 맞기 때문이다.
- VS Code에서 `fastapi` 아래에 노란 물결선이 떴다. `.venv`를 인터프리터로 선택하지 않아서 생기는 경고다.

## AI에게 질문한 내용

- Path Parameter와 Query Parameter를 어떻게 구분하는지
- `?name=kim&min_age=20`에서 파라미터가 몇 개인지
- 작업 중인 폴더(`phase02/chapter02`)와 열려 있던 `phase01` 탭이 왜 다른지
- `/courses` 혼자 해보기 코드 작성

## AI 답변 중 직접 검증한 부분

- Swagger에서 `GET /members/1`을 실행해 `200`과 회원 1명을 확인했다.
- 브라우저 주소창에서 `/members/abc`(422)와 `/members/99`(404)를 직접 요청해 응답 내용을 확인했다.
- Swagger에서 `GET /courses/filter/`에 `level=2`를 넣고 실행해 Request URL에 `?level=2`가 붙고 `200`이 나오는 것을 확인했다.
- `name`, `min_age`, `title` 검색 같은 나머지 경우는 AI가 보낸 요청 테스트로 확인했다.
  (`/courses/99` 404, `/courses/abc` 422, `?title=front` 200 등)
