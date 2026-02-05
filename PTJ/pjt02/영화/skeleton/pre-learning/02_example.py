# requests 사용 예시 2 : 알라딘 신간 도서 리스트 API 활용
import requests
from pprint import pprint


### request 방법 1: f-string을 사용한 URL 직접 생성 방식 ###

# API 요청에 필요한 파라미터들을 변수로 선언
ttbkey = '부여받은 TTBKey'  # 알라딘 API 인증 키
query_type = 'ItemNewSpecial'  # 신간 도서 요청 타입
max_results = 20  # 한 번에 받아올 결과 수
start = 1  # 검색 시작 위치
search_target = 'Book'  # 검색 대상(도서)
output = 'js'  # 출력 형식(json)
version = 20131101  # API 버전

# f-string을 사용하여 쿼리 파라미터가 포함된 전체 URL 생성
URL = f'http://www.aladin.co.kr/ttb/api/ItemList.aspx?ttbkey={ttbkey}&QueryType={query_type}&MaxResults={max_results}&start={start}&SearchTarget={search_target}&output={output}&Version={version}'

# 요청 보내기
response = requests.get(URL)

# JSON 형식의 응답을 파이썬 딕셔너리로 변환
response_dict = response.json()

# 전체 응답 데이터 출력
pprint(response_dict)


#############################################


### request 방법 2: params 매개변수를 사용한 방식 ###

# 기본 URL (쿼리 파라미터 제외)
URL = 'http://www.aladin.co.kr/ttb/api/ItemList.aspx'

# 쿼리 파라미터들을 딕셔너리로 구성
params = {
    'ttbkey': '부여받은 TTBKey',
    'QueryType': 'ItemNewAll',  # 모든 신간 도서 검색
    'MaxResults': 20,  # 최대 결과 수
    'start': 1,  # 시작 위치
    'SearchTarget': 'Book',  # 검색 대상
    'output': 'js',  # json 형식 출력
    'Version': '20131101',  # API 버전
}

# 요청 보내기 (params 매개변수 사용)
# requests가 자동으로 URL에 쿼리 파라미터를 추가하고 인코딩 처리
response = requests.get(URL, params=params).json()

# 응답에서 'item' 키의 값만 추출하여 출력
pprint(response.get('item'))
