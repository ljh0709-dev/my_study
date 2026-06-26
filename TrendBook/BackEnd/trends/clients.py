import httpx
from django.conf import settings


class TrendProviderError(RuntimeError):
    """뉴스·날씨 제공자 호출 실패."""


class _HTTPClient:
    def __init__(self, timeout=8.0, transport=None):
        self.timeout = timeout
        self.transport = transport

    def get_json(self, url, *, params=None, headers=None):
        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
                response = client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise TrendProviderError(f'외부 트렌드 API 호출에 실패했습니다: {exc}') from exc


class NaverNewsClient(_HTTPClient):
    URL = 'https://openapi.naver.com/v1/search/news.json'

    def search(self, query, display=5):
        if not settings.NAVER_CLIENT_ID or not settings.NAVER_CLIENT_SECRET:
            raise TrendProviderError('NAVER_CLIENT_ID/SECRET이 설정되지 않았습니다.')
        return self.get_json(
            self.URL,
            params={'query': query, 'display': max(1, min(display, 100)), 'sort': 'date'},
            headers={
                'X-Naver-Client-Id': settings.NAVER_CLIENT_ID,
                'X-Naver-Client-Secret': settings.NAVER_CLIENT_SECRET,
            },
        )


class OpenWeatherClient(_HTTPClient):
    URL = 'https://api.openweathermap.org/data/2.5/weather'

    def _api_params(self):
        if not settings.OPENWEATHER_API_KEY:
            raise TrendProviderError('OPENWEATHER_API_KEY가 설정되지 않았습니다.')
        return {
            'appid': settings.OPENWEATHER_API_KEY,
            'units': 'metric',
            'lang': 'kr',
        }

    def current(self, city=None):
        if not settings.OPENWEATHER_API_KEY:
            raise TrendProviderError('OPENWEATHER_API_KEY가 설정되지 않았습니다.')
        return self.get_json(self.URL, params={
            'q': city or settings.OPENWEATHER_CITY,
            'appid': settings.OPENWEATHER_API_KEY,
            'units': 'metric',
            'lang': 'kr',
        })

    def current_by_coordinates(self, lat, lon):
        return self.get_json(self.URL, params={
            **self._api_params(),
            'lat': lat,
            'lon': lon,
        })
