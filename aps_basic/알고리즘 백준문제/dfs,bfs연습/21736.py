import sys; sys.stdin = open('백준test.txt')
from collections import deque

def bfs(r,c):
    q = deque()
    q.append([r.c])
    visited[r][c] = 1
    people = 0

    while q:
        tr, tc = q.popleft()

        if arr[tr][tc] == 'P':
            people += 1

        for dr, dc in [[0,1], [1,0], [0,-1], [-1,0]]:
            nr = tr + dr
            nc = tc + dc
            if 0<=nr<N and 0<=nc<M and visited[nr][nc]==0 and arr[nr][nc] != 'X':
                q.append([nr,nc])
                visited[nr][nc] = 1
    return people

def find_do():
    for r in range(N):
        for c in range(M):
            if arr[r][c] == 'I':
                return r,c


N, M = map(int, input().split())
arr = [list(input()) for _ in range(N)]
# O는 빈 공간, X는 벽, I는 도연이, P는 사람
visited = [[0]*M for _ in range(N)]

r,c = find_do()

max_people = 0
max_people = max(max_people, bfs(r,c))
print(max_people)