import sys
sys.stdin = open('1851 정사각형 방_input.txt')
from collections import deque
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for _ in range(1,T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]

    # 상하좌우에 있는 다른 방으로 이동할 수 있다.
    # 이동하려는 방에 적힌 숫자가
    # 현재 방에 적힌 숫자보다 정확히 1 더 커야 한다.
    # 처음 어떤 수가 적힌 방에서 있어야
    # 가장 많은 개수의 방을 이동할 수 있는지

    cnt = 1
    room_num = 1000
    # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    dr = [0,1,0,-1]
    dc = [1,0,-1,0]
    def bfs(r,c):
        global cnt, room_num
        move = 1
        visited = [[0]*N for _ in range(N)]
        q = deque()
        q.append([r,c])

        while q:
            tr, tc = q.popleft()

            if cnt <= move:
                cnt = move
                room_num = min(arr[tr][tc], room_num)

            for d in range(4):
                nr = tr + dr[d]
                nc = tc + dc[d]
                if 0<=nr<N and 0<=nc<N and\
                        visited[nr][nc]==0 and\
                        arr[nr][nc] - arr[tr][tc] == 1:
                    q.append([nr,nc])
                    visited[nr][nc] = visited[tr][tc]+1
                    move += 1

    # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    for r in range(N):
        for c in range(N):
            bfs(r,c)

    print(f"#{_} {cnt} {room_num}")