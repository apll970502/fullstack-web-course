# Chapter 01 학습 기록

## Browser와 Web Server의 차이

Browser(Chrome)는 HTML을 받아서 화면에 보여주는 곳이고, Web Server는 그 HTML/CSS/JS 파일을 보내주는 곳이다.
이번 실습에서는 VS Code의 Live Server가 Web Server 역할을 했다.

## Web Server와 API Server의 차이

Web Server는 화면을 만드는 **파일**(HTML, CSS, JS, 이미지)을 주고, API Server는 **데이터**(JSON)를 준다.
1차에서는 Live Server(Web Server)와 강사 제공 API를 사용하고, 2차에서는 FastAPI로 API Server를 직접 만든다.

## localhost를 내가 이해한 방식

`http://127.0.0.1:5500` 에서 `127.0.0.1`(= localhost)은 내 컴퓨터 자신이고, `5500`은 Live Server가 사용하는 포트 번호다.
포트는 한 컴퓨터 안에서 여러 서버 프로그램을 구분하는 번호라고 이해했다.

## Network 탭에서 확인한 GET 요청

- `index.html` 요청: Method `GET`, Status `304` (이미 받은 파일이 바뀌지 않아서 캐시 사용)
- Disable cache를 체크하고 새로고침하면 Status `200`으로 바뀌는 것을 확인했다.
- `ws` (Status 101)는 Live Server가 자동 새로고침을 위해 연결한 것이다.

## LLM에게 질문한 내용

- F12를 눌러도 개발자 도구가 안 열리는 이유 → VS Code가 아니라 브라우저 창에서 눌러야 하고, `Ctrl + Shift + I`로도 열 수 있다.
- `git add` 명령어 뜻 → 커밋할 파일을 고르는(담는) 명령이다.
- Elements 탭에서 ▶ 버튼의 의미 → 접힌 HTML 요소를 펼쳐서 자식 요소를 보는 버튼이다.
- 결석한 1강 내용 정리 (Web Server와 API Server, localhost와 포트)

## 내가 직접 검증한 내용

- Live Server로 페이지를 열고 주소가 `http://127.0.0.1:5500/...`로 시작하는 것을 확인했다.
- Elements 탭에서 `<h1>Frontend 학습을 시작합니다.</h1>`를 확인했다.
- Network 탭에서 `index.html` GET 요청을 확인했다.
- `git push` 후 GitHub에서 파일이 올라간 것을 확인했다.
