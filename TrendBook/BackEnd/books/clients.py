import httpx
from django.conf import settings

from .models import MallType


class AladinAPIError(RuntimeError):
    """알라딘 API 호출 또는 응답 검증 실패."""


class AladinClient:
    BASE_URL = 'https://www.aladin.co.kr/ttb/api'
    SEARCH_TARGETS = {
        MallType.BOOK: 'Book',
        MallType.FOREIGN: 'Foreign',
        MallType.EBOOK: 'eBook',
    }

    def __init__(self, api_key=None, timeout=8.0, transport=None):
        self.api_key = api_key or settings.ALADIN_TTB_KEY
        self.timeout = timeout
        self.transport = transport

    def _get(self, endpoint, params):
        if not self.api_key:
            raise AladinAPIError('ALADIN_TTB_KEY가 설정되지 않았습니다.')

        common = {
            'ttbkey': self.api_key,
            'output': 'js',
            'Version': '20131101',
            'Cover': 'Big',
        }
        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
                response = client.get(f'{self.BASE_URL}/{endpoint}', params={**common, **params})
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AladinAPIError(f'알라딘 API 호출에 실패했습니다: {exc}') from exc

        if payload.get('errorCode'):
            raise AladinAPIError(payload.get('errorMessage') or '알라딘 API 오류')
        return payload

    def search(self, query, mall_type=MallType.BOOK, query_type='Keyword', start=1, max_results=20):
        return self._get('ItemSearch.aspx', {
            'Query': query,
            'QueryType': query_type,
            'SearchTarget': self.SEARCH_TARGETS[mall_type],
            'start': start,
            'MaxResults': max(1, min(max_results, 100)),
        })

    def lookup(self, isbn):
        return self._get('ItemLookUp.aspx', {
            'itemIdType': 'ISBN13',
            'ItemId': isbn,
        })

    def item_list(self, query_type='Bestseller', mall_type=MallType.BOOK,
                  category_id=None, start=1, max_results=50):
        params = {
            'QueryType': query_type,
            'SearchTarget': self.SEARCH_TARGETS[mall_type],
            'start': start,
            'MaxResults': max(1, min(max_results, 100)),
        }
        if category_id:
            params['CategoryId'] = category_id
        return self._get('ItemList.aspx', params)
