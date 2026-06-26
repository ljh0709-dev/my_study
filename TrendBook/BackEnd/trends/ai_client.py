import httpx
from django.conf import settings


class AIServiceError(RuntimeError):
    pass


class AIServiceClient:
    def __init__(self, timeout=5.0, transport=None):
        self.timeout = timeout
        self.transport = transport

    def submit(self, kind, payload):
        endpoints = {
            'trend': 'trends',
            'recommendation': 'recommendations',
            'article_recommendation': 'article-recommendations',
        }
        endpoint = endpoints.get(kind)
        if not endpoint:
            raise AIServiceError(f'Unsupported AI job kind: {kind}')
        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
                response = client.post(
                    f'{settings.FASTAPI_BASE_URL}/internal/v1/{endpoint}',
                    json=payload,
                    headers={'X-Internal-Secret': settings.INTERNAL_AI_SECRET},
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AIServiceError(f'AI 서비스 작업 접수 실패: {exc}') from exc

    def _post(self, endpoint, payload):
        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
                response = client.post(
                    f'{settings.FASTAPI_BASE_URL}/internal/v1/{endpoint}',
                    json=payload,
                    headers={'X-Internal-Secret': settings.INTERNAL_AI_SECRET},
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AIServiceError(f'AI 서비스 호출 실패({endpoint}): {exc}') from exc

    def embed(self, texts):
        return self._post('embeddings', {'texts': texts})

    def analyze_book(self, payload):
        return self._post('book-analysis', payload)
