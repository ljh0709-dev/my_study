# TrendBook AI Service

로컬 실행:

```powershell
uvicorn ai_service.app.main:app --host 127.0.0.1 --port 8001 --reload
```

- 상태 확인: `GET http://127.0.0.1:8001/health`
- 내부 추천 요청: `POST /internal/v1/recommendations`
- 내부 요청은 `.env`의 `INTERNAL_AI_SECRET` 값을 `X-Internal-Secret` 헤더로 전달해야 한다.

현재 Day 1 골격은 요청 검증과 비동기 접수까지만 수행한다. 실제 OpenAI 처리와 DRF 콜백은 Day 3 범위다.
