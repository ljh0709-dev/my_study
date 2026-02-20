import sys; sys.stdin = open("1226 미로1_input.txt")


def bfs(r, c, N):
    visited = [[0]*N for _ in range(N)]
    q = [[r,c]]
    visited[r][c] = 1

    while q:
        tr, tc = q.pop(0)
        if maze[tr][tc] == '3':
            return 1

        for dr, dc in [[0,1],[1,0],[0,-1],[-1,0]]:
            nr, nc = tr + dr, tc + dc
            if 0<=nr<N and 0<=nc<N and \
                    maze[nr][nc] != '1' and visited[nr][nc]==0:
                q.append([nr,nc])
                visited[nr][nc] = visited[tr][tc] + 1
    return 0


for test in range(1,11):
    _ = int(input())
    N = 16
    maze = [list(input()) for _ in range(N)]
    # 0: 길, 1: 벽, 2: 출발점, 3: 도착점

    # 시작점 찾기
    start_i, start_j = 0, 0
    for i in range(N):
        for j in range(N):
            if maze[i][j]=='2':
                start_i, start_j = i, j
                break
        if start_i and start_j:
            break

    ans = bfs(start_i, start_j, N)
    print(f"#{test} {ans}")