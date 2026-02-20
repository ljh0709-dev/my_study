import sys; sys.stdin = open("5102노드의거리_input.txt")

def bfs(V, S, G):
    visited = [0] * (V + 1)
    q = []
    q.append(S)
    visited[S] = 1

    while q:
        t = q.pop(0)

        if t == G:
            return visited[t] - 1

        for i in adj_list[t]:
            if not visited[i]:
                q.append(i)
                visited[i] = visited[t] + 1

    return 0


t = int(input())
for tc in range(1, t + 1):
    V, E = map(int, input().split())
    adj_list = [[] for _ in range(V + 1)]

    node = [list(map(int, input().split())) for _ in range(E)]
    for s, g in node:
        adj_list[s].append(g)
        adj_list[g].append(s)
    # print(adj_list)
    S, G = map(int, input().split())

    print(f"#{tc}", bfs(V, S, G))
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
# 강사님 풀이

# def bfs(v):
#     q = [v]
#     visited[v] = 1
#
#     while q:
#         t = q.pop(0)
#
#         if t == G:
#             return visited[t] - 1
#
#         for w in adj_list[t]:
#             if visited[w] == 0:
#                 q.append(w)
#                 visited[w] = visited[t] + 1
#     return 0
#
#
# t = int(input())
# for tc in range(1, t + 1):
#     V, E = map(int, input().split())
#     adj_list = [[] for _ in range(V + 1)]
#
#     for _ in range(E):
#         s, e = map(int, input().split())
#         adj_list[s].append(e)
#         adj_list[e].append(s)
#
#     S, G = map(int, input().split())
#
#     visited = [0] * (V+1)
#
#     print(f"#{tc} {bfs(S)}")