import sys
sys.stdin = open('5105 미로의 거리.txt')
from collections import deque

def bfs(r,c):
    q = deque()
    q.append([r,c])
    visited[r][c] = 1

    dr = [0,1,0,-1]
    dc = [1,0,-1,0]

    while q:
        tr, tc = q.popleft()
        # 목표지점에 도달하면 경로의 칸 수 반환
        if arr[tr][tc]=='3':
            return visited[tr][tc] - 2

        for d in range(4):
            nr = tr + dr[d]
            nc = tc + dc[d]
            if 0<=nr<N and 0<=nc<N and visited[nr][nc]==0 and arr[nr][nc]!='1':
                q.append([nr,nc])
                visited[nr][nc] = visited[tr][tc] + 1

    # 도달 못하면 0 반환
    return 0

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for _ in range(1,T+1):
    N = int(input())
    arr = [list(input()) for _ in range(N)]
    visited = [[0]*N for _ in range(N)]

    def find_start():
        for r in range(N):
            for c in range(N):
                if arr[r][c] == '2':
                    return r,c

    start_r, start_c = find_start()
    print(f"#{_} {bfs(start_r, start_c)}")

