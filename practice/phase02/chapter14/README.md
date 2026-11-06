# Chapter 14 — CORS · Frontend 연동 (1~3절 범위)

chapter13 의 `app` 을 복사해서 **CORSMiddleware** 를 추가하고, 브라우저에서 `GET /members` 를 호출하는 Frontend 페이지를 만들었다.
이번 범위: 강의 글 1~3절 (Origin / CORS 설정 / fetch 호출). 환경변수 분리(`CORS_ORIGINS`), 오류 일부러 재현(STEP 04), POST 연결(STEP 06)은 다음 범위.

## 구조
```
chapter14/
├─ app/                 chapter13 과 같은 Backend (+ CORS)
└─ frontend/index.html  fetch 로 GET /members 호출, 표로 출력
```

## 실행
Backend (chapter14 폴더에서)
```
python -m uvicorn app.main:app --reload
```
Frontend (chapter14/frontend 폴더에서, Live Server 를 써도 됨 — 포트 5500)
```
python -m http.server 5500
```
브라우저: `http://localhost:5500/index.html`

## Origin 비교
| | 주소 | Origin |
|---|---|---|
| Frontend | `http://localhost:5500` | scheme + host + **port 5500** |
| FastAPI | `http://localhost:8000` | scheme + host + **port 8000** |

포트가 달라 **다른 Origin** → 브라우저가 CORS 를 검사한다.

## CORS 설정 (`app/main.py`)
- `allow_origins = ["http://localhost:5500", "http://127.0.0.1:5500"]`
- `localhost` 와 `127.0.0.1` 은 브라우저가 서로 다른 Origin 으로 보므로 둘 다 적었다.
- `["*"]` 는 쓰지 않는다 (누가 호출할 수 있는지 설명 가능해야 함).

## 검증 결과
| 확인 | 결과 |
|---|---|
| 브라우저 화면 | "성공: 5명 (HTTP 200)", 표에 회원 5명 |
| 브라우저 Console | 회원 객체 5개 로그, 오류 없음 |
| 브라우저 Network | `GET http://localhost:8000/members → 200 OK` |
| 허용 Origin(5500) 응답 헤더 | `access-control-allow-origin: http://localhost:5500` |
| 허용하지 않은 Origin(3000) | 응답은 200 이지만 `access-control-allow-origin` 헤더 없음 → 브라우저가 응답 사용을 막음 |
| Preflight(OPTIONS, POST 사전 확인) | 200, 허용 메서드·헤더(`content-type`) 응답 |

- CORS 는 서버가 요청을 막는 기능이 아니라, **브라우저가 헤더를 보고 응답 사용을 제한**하는 정책이다. (3000 Origin 에도 서버는 200 으로 응답한다.)
- Frontend 는 값을 `textContent` 로 넣어 회원 이름이 HTML 로 해석되지 않게 했다.
- DB 비밀번호 등 Secret 은 Frontend 코드에 없다. 공개 값은 `API_BASE_URL` 뿐이다.

## 이번 범위 Definition of Done
- [x] Swagger 가 아닌 Browser 에서 GET /members 호출 성공
- [x] Browser Network 에서 200 확인
- [x] Origin 의 의미와 허용 Origin 설정 설명
- [x] 실제 Frontend Origin 만 허용 (`*` 미사용)
- [x] Browser 에 Secret 노출 없음
- [x] 허용하지 않은 Origin 으로 브라우저 CORS 오류 직접 확인 (STEP 04, 확인 후 설정 원복)
- [x] `127.0.0.1:5500` 으로 접속해도 허용 목록에 있어 성공함을 확인
- [ ] POST /members 연결과 DB 확인 (STEP 06)
- [ ] API Base URL / `CORS_ORIGINS` 환경별 분리 (5절)
- [x] Commit / Push
