import requests
from pprint import pprint

URL = 'https://api.themoviedb.org/3'
HEADERS = {
    'accept': 'application/json',
    'Authorization': 'Bearer <TMDB Access Token>',
}


def get_actor_genres(name):
    # 여기에 코드를 작성합니다.
    pass


if __name__ == '__main__':
    pprint(get_actor_genres('송강호'))
    pprint(get_actor_genres('봉준호'))
