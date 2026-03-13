import sys
sys.stdin = open('5102 노드의 거리.txt')
from collections import deque

def solve(v):
    q = deque()
    q.append(v)
    visited[v] = 0

    while q:
        t = q.popleft()
        if t == G:
            return visited[t]

        for w in adj_list[t]:
            if visited[w]==-1:
                q.append(w)
                visited[w] = visited[t] + 1

    return 0

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for _ in range(1,T+1):
    V, E = map(int, input().split())
    adj_list = [[] for _ in range(V+1)]
    visited = [-1]*(V+1)

    for i in range(E):
        S, G = map(int, input().split())
        adj_list[S].append(G)
        adj_list[G].append(S)

    S, G = map(int, input().split())

    print(f"#{_} {solve(S)}")

