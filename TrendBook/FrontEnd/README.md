# TrendBook Frontend

Vue 3, Vite, Pinia, Axios 기반 모바일 우선 클라이언트입니다. FastAPI를 직접 호출하지 않고 `VITE_API_BASE_URL`의 Django API만 사용합니다.

## 화면

- Perplexity Discover를 참고한 루트 랜딩, 트렌드 상세·추천 작업 폴링
- 도서 검색·상세·베스트셀러·찜
- 로그인·회원가입·마이페이지
- 독후감 목록·작성·상세·댓글

트렌드 상세는 네이버 제공 뉴스 요약과 원문 링크만 보여주며, RAG 벡터 유사도와 GPT 관련도 점수를 함께 표시합니다.

JWT access token 만료 시 refresh 요청은 한 번으로 합쳐지고, 갱신 실패 시 로컬 인증 상태를 지웁니다.

## 실행과 빌드

```powershell
npm ci
Copy-Item .env.example .env
npm run dev
npm run build
```
