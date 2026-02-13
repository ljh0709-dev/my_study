import sys
sys.stdin = open('연습문제2_전기버스_input.txt')

t = int(input())
for tc in range(1,t+1):
    k, n, m = map(int, input().split())
    m_list = list(map(int, input().split()))
    # k: 최대 이동 정류장
    # n: 종점
    # m: 충전기 설치된 정류장 수

    station = [0] * (n+1)
    for i in m_list:
        station[i] = 1

    charge = 0 # 충전 수
    now = 0 # 현재 정류장
    go = True # 종점 도착 가능 판단

    while now + k < n:
        max_idx = -1 # 가장 먼 정류장으로 위치 초기화
        for i in range(now+1, now+k+1): # 현시점 앞에 3정류장 체크
            if station[i] == 1: # 충전 정류장이면
                max_idx = i     # 최대거리 영점 조절
        now = max_idx           # 현위치 이동
        charge += 1             # 충전 냐미

        if max_idx == -1:       # 충전소 없으면
            go = False          # 못가요
            break

    if go:
        print(f'#{tc} {charge}')
    else:
        print(f'#{tc} 0')