# requests 사용 예시 1

# requests는 HTTP 요청을 보내는 파이썬 라이브러리
import requests

# pprint는 복잡한 데이터 구조를 보기 좋게 출력하는 라이브러리
from pprint import pprint


# API 요청을 보낼 주소(Endpoint)를 변수에 저장
# 이 API는 랜덤한 강아지 사진 URL을 반환합니다.
URL = 'https://dog.ceo/api/breeds/image/random'

# requests.get()으로 요청을 보내고, json()으로 응답을 파이썬 딕셔너리로 변환
response = requests.get(URL).json()
# 전체 응답 데이터 출력
# response에는 {'message': '강아지사진URL', 'status': 'success'} 형태의 데이터가 저장됨
pprint(response)

# 딕셔너리의 get 메서드로 'message' 키의 값(강아지 사진 URL)만 추출
results = response.get('message')
# 강아지 사진 URL만 출력
pprint(results)
