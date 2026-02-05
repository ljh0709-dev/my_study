import requests
from pprint import pprint


URL = 'https://api.themoviedb.org/3'
HEADERS = {
    'accept': 'application/json',
    'Authorization': f'Bearer <TMDB Access Token>',
}

def get_multi_search():
    # search movie API 문서: https://developer.themoviedb.org/reference/search-movie
    params = {
        'query': '범죄도시',  # 필수 파라미터
        'include_adult': True,
        'language': 'ko-KR',
        'page': 1,
    }

    # 요청 보내 받아온 결과는 requests 타입의 데이터이고, 파이썬에서 바로 쓸 수 없으며
    response = requests.get(f'{URL}/search/movie', headers=HEADERS, params=params)
    # 파이썬에서 쓸 수 있도록 하기 위해 json() 메서드를 사용해 json 타입의 데이터를 파이썬의 자료형으로 변환한다.
    response = response.json()
    # response 구조는 위의 공식 문서에서 확인할 수 있다.
    result = response.get('results')

    return result


if __name__ == '__main__':
    """
    "범죄도시" 키워드로 영화 검색
    """
    pprint(get_multi_search())
    """
    [{'adult': False,
      'backdrop_path': '/xord8lZ7mK8ctki6FBgNYrbpWCO.jpg',
      'genre_ids': [28, 80, 53],
      'id': 479718,
      'original_language': 'ko',
      'original_title': '범죄도시',
      'overview': '2004년 서울. 중국 하얼빈에서 활동하다 피신한 신흥 범죄조직의 악랄한 보스 장첸. 가리봉동  일대로 넘어온 '
                  '장첸과 그의 일당들은 단숨에 기존 조직들을 장악하고 가장 강력한 세력인 춘식이파 보스 황사 장까지 위협하며 도시 '
                  '일대의 최강자로 급부상한다. 한편 대한민국을 뒤흔든 장첸 일당을 잡기 위해 오직 주먹 한방으로 도시의 평화를 '
                  '유지해 온 괴물형사 마석도와  인간미 넘치는 든든한 리더 전일만 반장이 이끄는 강력반은 눈에는 눈 방식의  소탕 '
                  '작전을 기획하는데...',
      'popularity': 4.6135,
      'poster_path': '/ayk6y2D5v5VACFqrPfF05MARZ9n.jpg',
      'release_date': '2017-10-03',
      'title': '범죄도시',
      'video': False,
      'vote_average': 7.682,
      'vote_count': 472},
      ...
    ]
    """
