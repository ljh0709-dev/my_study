import os
import json
import time
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from dotenv import load_dotenv
from books.models import Book

class Command(BaseCommand):
    help = "알라딘 API 리스트를 호출하여 중복 없이 정확히 데이터를 수집하고 캐싱합니다."

    def handle(self, *args, **options):
        # 1. 환경 변수 설정
        env_path = os.path.join(settings.BASE_DIR, '.env')
        load_dotenv(dotenv_path=env_path)

        ttb_key = os.environ.get("ALADIN_TTB_KEY")
        if not ttb_key:
            self.stderr.write(self.style.ERROR(".env 파일에서 ALADIN_TTB_KEY를 찾을 수 없습니다."))
            return

        # 가장 안정적인 ItemList API로 다시 복귀
        url = "http://www.aladin.co.kr/ttb/api/ItemList.aspx"
        query_types = ['Bestseller', 'ItemNewAll']
        
        for q_type in query_types:
            self.stdout.write(f"--- '{q_type}' 데이터 수집 시작 ---")
            all_items = []      
            seen_isbns = set()  
            
            for page in range(1, 7):
                # 알라딘 최신 API 버전(20131101) 기준, ItemList의 start는 '페이지 번호(1,2,3...)'를 받습니다.
                params = {
                    'ttbkey': ttb_key,
                    'QueryType': q_type,
                    'MaxResults': 50,
                    'start': page,            # 1, 2, 3, 4, 5, 6 페이지 순차 호출
                    'SearchTarget': 'Book',
                    'output': 'js',
                    'Version': '20131101',
                    'Cover': 'MidBig'
                }

                try:
                    response = requests.get(url, params=params)
                    if response.status_code != 200:
                        self.stderr.write(f"API 요청 실패 (Status Code: {response.status_code})")
                        continue
                    
                    data = response.json()
                    items = data.get('item', [])
                    
                    if not items:
                        self.stdout.write(self.style.WARNING(f"  {page}페이지: 더 이상 데이터가 없습니다. 루프를 종료합니다."))
                        break
                    
                    page_new_items = []
                    duplicate_count = 0
                    
                    for item in items:
                        isbn = item.get('isbn13') or item.get('isbn')
                        
                        if not isbn:
                            continue
                            
                        if isbn in seen_isbns:
                            duplicate_count += 1
                            continue
                        
                        page_new_items.append(item)
                        seen_isbns.add(isbn)
                    
                    # [핵심] API가 파라미터를 무시하고 1페이지 데이터만 계속 똑같이 던져주는 경우 예외 처리
                    # 가져온 50개 전부가 이미 이전에 다 본 중복 데이터라면 API가 페이징을 지원하지 않는 것입니다.
                    if duplicate_count == len(items) and len(items) > 0:
                        self.stdout.write(self.style.WARNING(f"  {page}페이지: API가 동일한 데이터를 반복 반환하고 있습니다. 수집을 강제 중단합니다."))
                        break
                    
                    if page_new_items:
                        self.sync_to_db(page_new_items)
                        all_items.extend(page_new_items)
                        self.stdout.write(f"  {page}페이지 완료: 신규 {len(page_new_items)}개 추가 (누적: {len(all_items)}개)")
                    
                    time.sleep(0.5)

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"에러 발생 ({q_type} - {page}페이지): {str(e)}"))

            # 최종 수집된 고유 데이터만 저장
            self.save_to_json(all_items, q_type)
            self.stdout.write(self.style.SUCCESS(f"'{q_type}' 총 {len(all_items)}개 동기화 완료\n"))

    def sync_to_db(self, items):
        """데이터를 DB에 저장하는 로직"""
        for item in items:
            isbn = item.get('isbn13') or item.get('isbn')
            if not isbn: 
                continue

            pub_date_raw = item.get('pubDate')
            pub_date = None
            if pub_date_raw:
                try:
                    pub_date = datetime.strptime(pub_date_raw, "%Y-%m-%d").date()
                except ValueError:
                    pass

            Book.objects.update_or_create(
                isbn=isbn,
                defaults={
                    'title': item.get('title', ''),
                    'author': item.get('author', ''),
                    'publisher': item.get('publisher', ''),
                    'cover_img': item.get('cover'),
                    'description': item.get('description', ''),
                    'category_name': item.get('categoryName', ''),
                    'aladin_link': item.get('link'),
                    'pub_date': pub_date,
                }
            )

    def save_to_json(self, items, q_type):
        """누적된 데이터를 JSON 파일로 저장"""
        filename = f"books_{q_type}_total.json"
        path = os.path.join(settings.BASE_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=4)
        self.stdout.write(f"  로컬 파일 저장 완료: {filename}")