import heapq

arr = [20, 15, 19, 4, 13, 11]

# 1. 기본 리스트를 heap 으로 만들기
# heapq.heapify(arr)  # 최소힙으로 바뀐다.
# 디버깅 시에 이진 트리로 그림을 그려야 한다!
# -> 딱 봤을때는 정렬이 안된 것 처럼 보인다.
# print(arr)

# 2. 하나 씩 데이터를 추가
min_heap = []
for num in arr:
    heapq.heappush(min_heap, num)
print(min_heap)

# 최대힙
max_heap = []
for num in arr:
    # 음수로 바꿔서 집어넣어준다
    # - 숫자가 클수록 작은 값
    heapq.heappush(max_heap, -num)

# 꺼낼 때 다시 음수를 곱해준다.
while max_heap:
    pop_num = heapq.heappop(max_heap)
    print(-pop_num, end=' ')

# ------------------ 전자사전 예제
# 1. 길이 순서로 먼저 출력
# 2. 길이가 같다면, 사전 순으로 출력

arr = ['apple', 'banana', 'kiwi', 'abcd', 'abca', 'lemon', 'peach', 'grape', 'pear']
# sort 를 쓰면 아래와 같다.
# 즉, 우선순위가 2가지
# arr.sort(key=lambda x: (len(x), x))
dictionary = []

# 단어를 삽입 (길이, 단어) 형태로 삽입
for word in arr:
    heapq.heappush(dictionary, (len(word), word))

# 전자사전에서 단어를 하나씩 꺼내기
print("전자사전 순서:")
while dictionary:
    length, word = heapq.heappop(dictionary)
    print(f"{word} (길이: {length})")

# -------------------- 우선순위가 여러 개라면

print("--------------------------------")

import heapq


class Patient:
    def __init__(self, name, criticality, age, arrival_time):
        self.name = name
        self.criticality = criticality  # 1~5 (5가 가장 위급)
        self.age = age
        self.arrival_time = arrival_time  # 접수 순서 (작을수록 먼저 옴)

    # __lt__: 인스턴스들의 우선순위를 비교할 때 호출하는 메직 메서드
    def __lt__(self, other):
        # 1순위: 위급도 (내림차순 - 높은 숫자가 우선순위가 높음)
        if self.criticality != other.criticality:
            return self.criticality > other.criticality

        # 2순위: 나이 (내림차순 - 고령자 우선)
        if self.age != other.age:
            return self.age > other.age

        # 3순위: 먼저 온 순서 (오름차순 - 도착 시간이 빠를수록 우선)
        return self.arrival_time < other.arrival_time

    def __repr__(self):
        return f"[{self.name}] 위급:{self.criticality}, 나이:{self.age}, 도착:{self.arrival_time}"


# 환자 명단
patients = [
    Patient("김철수", 3, 40, 10),  # 평범한 위급도
    Patient("이영희", 5, 70, 11),  # 매우 위급, 고령 (최우선)
    Patient("박민수", 3, 80, 12),  # 철수와 위급도 같지만 나이가 더 많음
    Patient("최지우", 5, 20, 13),  # 영희와 위급도 같지만 나이가 적음
    Patient("정본캐", 3, 40, 9)  # 철수와 위급도/나이 같지만 더 먼저 옴
]

# 힙 구성
pq = []
for p in patients:
    heapq.heappush(pq, p)

# 진료 순서대로 출력
print("응급실 진료 순서")
while pq:
    print(heapq.heappop(pq))
