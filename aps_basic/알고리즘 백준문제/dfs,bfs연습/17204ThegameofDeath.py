import sys
input = sys.stdin.readline
from collections import deque

def bfs(v):
    q = deque()
    q.append([v,0])
    visited[v] = 1

    while q:
        t, call = q.popleft()
        if t == K:
            return call

        for w in adj_list[t]:
            if visited[w]==0:
                q.append([w, call+1])
                visited[w] = 1
    return -1


N, K = map(int, input().split())
# N: 인원 수, M: 보성이
adj_list = [[] for _ in range(N)]
visited = [0]*N

for i in range(N):
    pick = int(input())
    adj_list[i].append(pick)

answer = bfs(0)
print(answer)