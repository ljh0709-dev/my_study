import sys; sys.stdin = open("1219길찾기_input.txt")


def dfs(v):
    visited[v] = 1

    for w in adj_list[v]:
        if w == 99:
            return 1
        else:
            if visited[w] == 0:
                if dfs(w) == 1:
                    return 1
    return 0



for _ in range(10):
    tc, N = map(int, input().split())
    arr = list(map(int, input().split()))

    adj_list = [[] for _ in range(N + 1)]  # 인접리스트
    visited = [0] * (N + 1)  # 방문리스트

    
    for i in range(N):
        start, end = arr[2*i], arr[2*i + 1]
        adj_list[start].append(end)     # 단일 방향


    print(f"#{tc} {dfs(0)}")
        