import sys
sys.stdin = open('연습문제3_input.txt')


def dfs(v):     # 시작 정점
    global cnt
    # 방문 체크(v) + 할 일
    visited[v] = 1
    cnt += 1
    print(v, end=' ')
    # v의 인접 정점 w -> 미방문이면 dfs(w)
    for w in adj_list[v]:
        if visited[w] == 0:     # 방문 안했으면
            dfs(w)



##############################
V, E = map(int, input().split())    # V: 정점 수, E: 간선 수
adj_list = [[] for _ in range(V+1)] # 인접리스트
visited = [0] * (V+1)               # 방문리스트

temp = list(map(int, input().split()))  # 간선 양 끝 정점

for i in range(E):      # 간선의 개수만큼 반복
    start, end = temp[2*i], temp[2*i+1]     # temp[2*i : 2*i + 2]
    adj_list[start].append(end)
    adj_list[end].append((start))       # 양방향일 때만 함.

cnt = 0
dfs(1)
print()
print(cnt)