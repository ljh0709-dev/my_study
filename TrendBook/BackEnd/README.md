# TrendBook Backend

Django REST Framework가 인증·DB·뉴스·도서·벡터 캐시·검증을 소유하고, FastAPI가 OpenAI 호출만 담당합니다.

## AI 경계

- `ai_service/app/openai_adapter.py`: GPT-5.4-mini Responses API strict JSON Schema, embeddings API, 재시도와 응답 검증
- `POST /internal/v1/trends`: 뉴스 15~60건에서 주제 5개 생성
- `POST /internal/v1/recommendations`: RAG 후보 20권 안에서 추천 5권 생성
- `POST /internal/v1/embeddings`: 도서·질의 임베딩
- `POST /internal/v1/book-analysis`: 도서 관심 요인과 제공된 리뷰 발췌 요약
- 모든 내부 API는 `X-Internal-Secret`을 요구합니다.

기사 ID와 ISBN은 요청마다 JSON Schema enum으로 제한하며, Django 콜백에서도 허용 목록·중복·개수를 재검증합니다. GPT 작업 실패 시 새 배치를 공개하지 않고 직전 성공 배치를 유지합니다.

## RAG

`BookEmbedding`은 도서 메타데이터의 콘텐츠 해시, 모델, 차원, JSON 벡터를 저장합니다. SQLite 데모 규모에서는 Python 코사인 유사도 검색을 사용합니다.

```powershell
python manage.py sync_book_embeddings --batch-size 50
```

트렌드 제목·요약·키워드·관련 기사 문맥을 임베딩해 상위 20권을 검색하고, 판매지수·랭킹을 낮은 가중치로 더합니다. 최종 추천에는 `retrieval_score`와 `embedding_model`이 저장됩니다.

## 리뷰 요약

도서 분석 API는 제공된 `review_excerpts`만 리뷰 근거로 사용합니다. 발췌가 없으면 리뷰 경향을 추측하지 않고 본문 부재를 명시합니다. 같은 입력 해시는 캐시를 재사용합니다.

## 실행·테스트

루트 [README](../README.md)의 실행 순서를 따르세요.

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python -m unittest discover ai_service.tests -v
```
