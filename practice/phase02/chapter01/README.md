# Phase 02 Chapter 01 학습 기록

## 내가 정의한 API Contract

### 회원 목록 조회 (수업 예제)

| 항목 | 약속 |
|---|---|
| Method / Path | `GET /members` |
| Request Body | 없음 |
| Success Status | `200 OK` |
| Response | `id`, `name`, `email`을 가진 회원 객체의 배열(JSON) |

### 강좌 목록 조회 (혼자 해보기)

| 항목 | 약속 |
|---|---|
| Method / Path | `GET /courses` |
| Request Body | 없음 |
| Success Status | `200 OK` |
| Response | `id`, `title`, `instructor`를 가진 강좌 객체의 배열, 최소 3개 |

## Uvicorn의 역할

FastAPI 애플리케이션(`main:app`)을 실제 HTTP 서버로 실행한다.
브라우저의 HTTP 요청을 받아 FastAPI에 넘겨 주고, 결과를 응답으로 돌려준다.
`--reload` 옵션으로 코드를 저장하면 서버가 자동으로 다시 시작된다.

## FastAPI의 역할

어떤 요청(Method + Path)을 어떤 Python 함수가 처리할지 연결(Route)하고,
함수가 반환한 데이터를 JSON 응답으로 만든다. `/docs`에 Swagger UI 문서도 자동으로 만들어 준다.

## Swagger에서 확인한 Evidence

| 대상 | Request URL | Method | Code | Response Body |
|---|---|---|---|---|
| members | `http://127.0.0.1:8000/members` | GET | 200 | Kim, Lee 두 명의 JSON 배열 |
| courses | `http://127.0.0.1:8000/courses` | GET | 200 | Database, Frontend, Backend 세 강좌의 JSON 배열 |

- 응답 헤더: `content-type: application/json`, `server: uvicorn`
- 브라우저 주소창(`/members`, `/courses`)에서도 같은 JSON이 보였다.
- DevTools Network 탭에서 `members` 요청의 Request Method `GET`, Status Code `200 OK`를 확인했다.

## 발생한 오류와 해결 과정

- `cd practice\phase02\chapter01` 실행 시 "경로는 존재하지 않으므로 찾을 수 없습니다" 오류가 났다.
  원인은 이미 `chapter01` 폴더 안에 있는 상태에서 상대 경로로 다시 이동하려 했기 때문이다.
  현재 위치를 확인하고, 필요하면 전체 경로로 이동해서 해결했다.
- `/favicon.ico`가 `404 Not Found`로 터미널에 찍혔다. 브라우저가 탭 아이콘을 자동으로 요청한 것이라 오류가 아니다.
- VS Code에서 `fastapi` import에 노란 물결선이 떴다. VS Code가 가상환경(`.venv`)을 인터프리터로 선택하지 않아서 생기는 경고였다.

## AI에게 질문한 내용

- 실습 순서와 각 단계의 의미(가상환경, Uvicorn, Swagger)
- 터미널 로그 읽는 법 (`200 OK`, `404 Not Found`, `Reloading`)
- 혼자 해보기 `GET /courses`를 무엇으로 만들어야 하는지

## AI 답변 중 내가 직접 검증한 부분

- AI가 만든 `/courses` 코드가 Contract(Method, Path, 상태 코드, 응답 구조, 3개 이상)와 맞는지
  Swagger Execute와 브라우저 주소창에서 직접 확인했다.
- `--reload`가 동작하는지 터미널의 `StatReload detected changes ... Reloading` 로그로 확인했다.
