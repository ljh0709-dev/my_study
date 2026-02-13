import sys; sys.stdin = open('4875미로_input.txt')
# 4방향 + dfs
# dfs(r,c):
# visited[r][c] = True
# for d in range(4):
# nr = r + dr[d]
# nc = c + dc[d]
# 인덱스체크, 벽 체크, 방문체크,
# if 0<=nr<N and 0<=nc<N and visited[nr][nc]==False:
#   if arr[nr][nc] == 3:
#       return 1
#   elif arr[nr][nc] == 0:
#       if dfs(nr,nc) == 1:
#           return 1


def dfs(r, c):
    visited[r][c] = True

    for d in range(4):
        nr = r + di[d]
        nc = c + dj[d]
        if 0 <= nr < N and 0 <= nc < N and visited[nr][nc] == False:
            if maze[nr][nc] == 3:
                return 1
            else:
                if maze[nr][nc] == 0:
                    if dfs(nr, nc) == 1:
                        return 1
    return 0


####################
t = int(input())
for tc in range(1, t + 1):
    N = int(input())
    maze = [list(map(int, input())) for _ in range(N)]

    visited = [[False] * N for _ in range(N)]

    # 시작점 찾기
    start_i = 0
    start_j = 0
    for i in range(N):
        for j in range(N):
            if maze[i][j] == 2:
                start_i = i
                start_j = j
                break
        if start_i:
            break

    di = [0, 1, 0, -1]
    dj = [1, 0, -1, 0]

    print(f"#{tc} {dfs(start_i, start_j)}")


