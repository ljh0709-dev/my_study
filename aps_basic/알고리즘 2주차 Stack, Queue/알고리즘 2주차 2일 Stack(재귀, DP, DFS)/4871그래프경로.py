import sys; sys.stdin = open('4871그래프경로_input.txt')


def dfs(S, G):
    visited[S] = 1

    for w in adj_list[S]:
        if w == G:
            return 1
        else:
            if visited[w] == 0:
                if dfs(w, G) == 1:
                    return 1
    return 0


t = int(input())
for tc in range(1,t+1):
    V, E = map(int, input().split())    # V: 정점 수, E: 간선 수
    adj_list = [[] for _ in range(V+1)] # 인접리스트
    visited = [0] * (V+1)   # 방문리스트

    node = [list(map(int, input().split())) for _ in range(E)]
    for s,g in node:
        adj_list[s].append(g)

    S, G = map(int, input().split())

    print(f"#{tc} {dfs(S,G)}")

