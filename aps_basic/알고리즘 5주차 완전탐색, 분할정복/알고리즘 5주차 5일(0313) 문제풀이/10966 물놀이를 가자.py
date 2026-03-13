import sys
sys.stdin = open('10966 물놀이를 가자_input.txt')
from collections import deque

def bfs():
    dr = [0,1,0,-1]
    dc = [1,0,-1,0]

    q = deque()
    for r in range(N):
        for c in range(M):
            if arr[r][c] == 'W':
                q.append([r,c])
                visited[r][c] = 0

    while q:
        # W의 위치를 q에 먼저 다 넣어놓았기 때문에, 각 W 기준으로 퍼져나감
        tr, tc = q.popleft()

        for d in range(4):
            nr = tr + dr[d]
            nc = tc + dc[d]
            if 0<=nr<N and 0<=nc<M and visited[nr][nc] == -1 and arr[nr][nc]=='L':
                q.append([nr,nc])
                visited[nr][nc] = visited[tr][tc] + 1
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for _ in range(1,T+1):
    N, M = map(int, input().split())
    arr = [list(input()) for _ in range(N)]
    visited = [[-1] * M for _ in range(N)]

    move = 0
    bfs()
    # for i in visited:
    #     print(i)

    for i in range(N):
        for j in range(M):
            if arr[i][j] == 'L':
                move += visited[i][j]

    print(f"#{_} {move}")