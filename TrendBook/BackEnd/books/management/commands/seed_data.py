"""
TrendBook 테스트 데이터 시드 커맨드.
실행: python manage.py seed_data
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from books.models import Book, BookBookmark
from trends.models import TrendIssue
from recommendations.models import Recommendation
from ai.models import AISummary


class Command(BaseCommand):
    help = 'TrendBook DB에 테스트 데이터를 합성하여 삽입합니다.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('=== TrendBook Seed Data ==='))

        # ── 1. Users (5명) ──
        users_data = [
            {'username': 'hyomin', 'email': 'hyomin@trendbook.com', 'nickname': '효민', 'preferred_genres': '소설,과학'},
            {'username': 'jihoon', 'email': 'jihoon@trendbook.com', 'nickname': '지훈', 'preferred_genres': '경제,자기계발'},
            {'username': 'sooyeon', 'email': 'sooyeon@trendbook.com', 'nickname': '수연', 'preferred_genres': '역사,문화'},
            {'username': 'minjae', 'email': 'minjae@trendbook.com', 'nickname': '민재', 'preferred_genres': '기술,IT'},
            {'username': 'eunji', 'email': 'eunji@trendbook.com', 'nickname': '은지', 'preferred_genres': '에세이,여행'},
        ]
        users = []
        for ud in users_data:
            user, created = User.objects.get_or_create(
                email=ud['email'],
                defaults={
                    'username': ud['username'],
                    'nickname': ud['nickname'],
                    'preferred_genres': ud['preferred_genres'],
                },
            )
            if created:
                user.set_password('test1234!')
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f'  [OK] Users: {len(users)}명'))

        # ── 2. Books (10권) ──
        books_data = [
            {'isbn': '9788936434120', 'title': '채식주의자', 'author': '한강', 'publisher': '창비',
             'description': '한 여자가 어느 날 갑자기 채식을 시작하면서 벌어지는 이야기.', 'category_name': '소설',
             'pub_date': '2007-10-30'},
            {'isbn': '9788932917245', 'title': '모순', 'author': '양귀자', 'publisher': '쓰다',
             'description': '어떤 사람의 한 주를 따라가며 그 속에 숨겨진 모순을 발견하는 이야기.',
             'category_name': '소설', 'pub_date': '2013-07-15'},
            {'isbn': '9791191114225', 'title': '역행자', 'author': '자청', 'publisher': '웅진지식하우스',
             'description': '부의 추월차선을 위한 7단계 자기 혁명.', 'category_name': '자기계발',
             'pub_date': '2022-06-01'},
            {'isbn': '9788901260716', 'title': '트렌드 코리아 2024', 'author': '김난도 외', 'publisher': '미래의창',
             'description': '2024년 대한민국 소비 트렌드 전망.', 'category_name': '경제/경영',
             'pub_date': '2023-10-20'},
            {'isbn': '9791168340510', 'title': '불편한 편의점', 'author': '김호연', 'publisher': '나무옆의자',
             'description': '서울 한복판 편의점에서 벌어지는 따뜻한 이야기.', 'category_name': '소설',
             'pub_date': '2021-04-20'},
            {'isbn': '9788972757719', 'title': '사피엔스', 'author': '유발 하라리', 'publisher': '김영사',
             'description': '인류의 역사와 문명의 발전을 추적하는 대작.', 'category_name': '역사',
             'pub_date': '2015-11-23'},
            {'isbn': '9791190030915', 'title': '클린 코드', 'author': '로버트 C. 마틴', 'publisher': '인사이트',
             'description': '깨끗한 코드를 작성하기 위한 실전 가이드.', 'category_name': 'IT/프로그래밍',
             'pub_date': '2013-12-24'},
            {'isbn': '9788934972464', 'title': '총 균 쇠', 'author': '재레드 다이아몬드', 'publisher': '문학사상',
             'description': '인류 문명의 불균형을 환경과 지리로 설명하는 명저.', 'category_name': '과학',
             'pub_date': '2005-12-19'},
            {'isbn': '9791164050826', 'title': 'AI 2041', 'author': '리카이푸, 천추판', 'publisher': '한빛비즈',
             'description': '2041년 AI가 바꿀 미래를 10가지 이야기로 풀어낸 책.', 'category_name': 'IT/프로그래밍',
             'pub_date': '2022-02-07'},
            {'isbn': '9788960518384', 'title': '나미야 잡화점의 기적', 'author': '히가시노 게이고', 'publisher': '현문미디어',
             'description': '한 잡화점에서 벌어지는 기적 같은 상담 이야기.', 'category_name': '소설',
             'pub_date': '2012-11-20'},
        ]
        books = []
        for bd in books_data:
            pub_date = bd.pop('pub_date')
            book, _ = Book.objects.get_or_create(
                isbn=bd['isbn'],
                defaults={**bd, 'pub_date': pub_date},
            )
            books.append(book)
        self.stdout.write(self.style.SUCCESS(f'  [OK] Books: {len(books)}권'))

        # ── 3. TrendIssues (10건) ──
        now = timezone.now()
        trends_data = [
            {'title': '한-미 정상회담 개최 예정', 'summary': '한-미 정상이 워싱턴에서 정상회담을 가질 예정이다. 양국 간 경제·안보 협력이 핵심 의제로 논의될 전망이다.',
             'category': 'POLITICS', 'source': 'Google News RSS'},
            {'title': '한국은행 기준금리 동결', 'summary': '한국은행이 기준금리를 현 수준에서 동결했다. 물가 안정과 가계부채 관리를 고려한 결정이다.',
             'category': 'ECONOMY', 'source': '네이버 뉴스'},
            {'title': 'GPT-5 출시 임박', 'summary': 'OpenAI가 GPT-5 모델 출시를 앞두고 있다. 멀티모달 성능과 추론 능력이 대폭 강화될 것으로 보인다.',
             'category': 'TECH', 'source': 'TechCrunch'},
            {'title': '칸 영화제 한국 영화 2편 진출', 'summary': '제79회 칸 영화제 경쟁 부문에 한국 영화 2편이 진출했다.',
             'category': 'CULTURE', 'source': 'Google News RSS'},
            {'title': '전국 폭염 특보 발령', 'summary': '기상청이 전국 대부분 지역에 폭염 특보를 발령했다. 낮 최고 기온이 35도를 넘는 지역이 속출하고 있다.',
             'category': 'WEATHER', 'source': '기상청'},
            {'title': '국회 예산안 심의 본격화', 'summary': '국회가 내년도 예산안 심의에 본격 돌입했다. 복지·국방 분야 예산 배분이 쟁점이다.',
             'category': 'POLITICS', 'source': '네이버 뉴스'},
            {'title': '비트코인 10만 달러 돌파', 'summary': '비트코인이 사상 최초로 10만 달러를 돌파했다. 기관 투자자 유입이 주요 원인으로 분석된다.',
             'category': 'ECONOMY', 'source': 'Bloomberg'},
            {'title': '삼성 6G 칩 시연 성공', 'summary': '삼성전자가 세계 최초로 6G 통신 칩 시연에 성공했다.',
             'category': 'TECH', 'source': 'Google News RSS'},
            {'title': 'K-POP 그룹 빌보드 1위', 'summary': '한국 아이돌 그룹이 빌보드 Hot 100 차트에서 1위를 차지했다.',
             'category': 'CULTURE', 'source': '네이버 뉴스'},
            {'title': '수도권 집중호우 예보', 'summary': '내일 수도권에 시간당 50mm 이상의 집중호우가 예보되었다.',
             'category': 'WEATHER', 'source': '기상청'},
        ]
        trends = []
        for i, td in enumerate(trends_data):
            trend, _ = TrendIssue.objects.get_or_create(
                title=td['title'],
                defaults={
                    'summary': td['summary'],
                    'category': td['category'],
                    'source': td['source'],
                },
            )
            trends.append(trend)
        self.stdout.write(self.style.SUCCESS(f'  [OK] TrendIssues: {len(trends)}건'))

        # ── 4. AISummary (도서 5권에 대한 AI 요약) ──
        ai_data = [
            {'book': books[0], 'sales_reason': '노벨문학상 수상작으로 세계적 관심이 급증.', 'review_summary': '강렬하고 상징적인 서사가 인상적이라는 평이 다수.', 'status': 'completed'},
            {'book': books[2], 'sales_reason': '자기계발서 베스트셀러 1위 유지.', 'review_summary': '실행 가능한 단계별 전략이 좋다는 평이 많음.', 'status': 'completed'},
            {'book': books[3], 'sales_reason': '연말 트렌드 도서로 기업인·마케터 필독서.', 'review_summary': '매년 트렌드를 정리해주는 시리즈로 신뢰도가 높음.', 'status': 'completed'},
            {'book': books[6], 'sales_reason': '개발자 필독서로 꾸준한 수요.', 'review_summary': '코드 품질 향상에 실질적 도움이 된다는 후기가 다수.', 'status': 'completed'},
            {'book': books[8], 'sales_reason': 'AI 미래 전망에 대한 관심 증가.', 'review_summary': '소설 형식의 구성이 접근하기 쉽다는 긍정 평가.', 'status': 'pending'},
        ]
        ai_count = 0
        for ad in ai_data:
            _, created = AISummary.objects.get_or_create(
                book=ad['book'],
                defaults={
                    'sales_reason': ad['sales_reason'],
                    'review_summary': ad['review_summary'],
                    'status': ad['status'],
                },
            )
            if created:
                ai_count += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] AISummary: {ai_count}건'))

        # ── 5. Recommendations (트렌드 ↔ 도서 매핑 15건) ──
        rec_data = [
            # 정치 이슈 → 역사/사회 도서
            (trends[0], books[5], '한-미 관계를 이해하기 위한 문명사적 관점의 필독서.'),
            (trends[0], books[7], '국제 관계와 지정학적 배경을 이해하는 데 도움.'),
            (trends[5], books[5], '예산 정치의 역사적 맥락을 이해하는 참고서.'),
            # 경제 이슈 → 경제/자기계발 도서
            (trends[1], books[3], '금리 정책과 소비 트렌드의 연관성을 분석.'),
            (trends[1], books[2], '경제 불확실성 속 개인 재무 전략을 제시.'),
            (trends[6], books[3], '디지털 자산 트렌드를 소비 관점에서 분석.'),
            (trends[6], books[2], '투자와 자기계발을 연결하는 실천 전략.'),
            # 기술 이슈 → IT/과학 도서
            (trends[2], books[8], 'AI 발전의 미래를 구체적 시나리오로 전망.'),
            (trends[2], books[6], 'AI 시대에도 변하지 않는 코드 품질의 가치.'),
            (trends[7], books[8], '6G와 AI 융합이 만들어낼 미래 사회상.'),
            # 문화 이슈 → 소설/문화 도서
            (trends[3], books[0], '한국 문학의 세계적 위상을 보여주는 대표작.'),
            (trends[3], books[4], '한국 일상을 따뜻하게 그린 국민 소설.'),
            (trends[8], books[9], '문화 콘텐츠와 감동적 스토리텔링의 만남.'),
            # 날씨 이슈 → 에세이/생활 도서
            (trends[4], books[1], '무더위 속 내면의 모순을 들여다보는 시간.'),
            (trends[9], books[4], '비 오는 날 읽기 좋은 따뜻한 이야기.'),
        ]
        rec_count = 0
        for trend, book, reason in rec_data:
            _, created = Recommendation.objects.get_or_create(
                trend=trend,
                book=book,
                defaults={'ai_recommend_reason': reason},
            )
            if created:
                rec_count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✅ Recommendations: {rec_count}건'))

        # ── 6. BookBookmarks (찜하기 — 사용자별 2~4권) ──
        bookmark_count = 0
        for user in users:
            sample_books = random.sample(books, random.randint(2, 4))
            for book in sample_books:
                _, created = BookBookmark.objects.get_or_create(
                    user=user, book=book,
                )
                if created:
                    bookmark_count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✅ BookBookmarks: {bookmark_count}건'))

        self.stdout.write(self.style.MIGRATE_HEADING('=== Seed 완료 ==='))
