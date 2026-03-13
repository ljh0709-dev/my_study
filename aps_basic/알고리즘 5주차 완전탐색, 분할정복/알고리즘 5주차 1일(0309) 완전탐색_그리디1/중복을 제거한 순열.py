path = []
visited = [0]*3        # 사용한 숫자인지 구분하는 방문 체크 리스트

def recur(cnt):
    if cnt == 2:
        print(path)
        return
    # 한 번의 선택에서 3가지 경우의 수
    for i in range(3):
        # [주 의] in은 O(N)이라서 시간복잡도 느리기 때문에 시간초과 가능성 높음
        if visited[i]:  # 이미 i를 사용한 적이 있으면 (검사코드)
            continue    # 재귀호출 생략

        visited[i] = 1  # 방문체크
        path.append(i)
        recur(cnt + 1)
        path.pop()
        visited[i] = 0  # 방문 초기화
recur(0)
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# 중복순열과 순열 구현하기
# N개의 주사위를 던져 나올 수 있는 모든 중복 순열(type1)과 순열(type2) 출력
path2 = []
visited2 = [0]*7         # 사용한 숫자인지 구분하는 방문 체크 리스트

def recur2(cnt):
    if cnt == 2:
        print(path2)
        return

    for i in range(1,7):
        if visited2[i]:  # 이미 i를 사용한 적이 있으면 (검사코드)
            continue    # 재귀호출 생략

        visited2[i] = 1  # 방문체크
        path2.append(i)
        recur2(cnt + 1)
        path2.pop()
        visited2[i] = 0  # 방문 초기화
recur2(0)