import sys
sys.stdin = open('test_input.txt')


def dfs(r, c, count):
    global cnt

    # 도착하면 리턴
    if r == N-1 and c == M-1:
        cnt = min(cnt, count)
        return

    # 방문 체크
    visited[r][c] = True

    for d in range(4):
        nr = r + di[d]
        nc = c + dj[d]
        if 0 <= nr < N and 0 <= nc < M:     # 미로 범위 안
            if maze[nr][nc] == 1 and visited[nr][nc] == False:  # 길이고, 간 적 없으면
                visited[nr][nc] = True  # 방문 체크
                dfs(nr, nc, count + 1)  # 옮긴 위치 돌림
                visited[nr][nc] = False # 막다른 길이면 돌아가기

    return 0


####################
t = int(input())
for tc in range(1,t+1):
    N, M = map(int, input().split())
    maze = [list(map(int, input())) for _ in range(N)]

    visited = [[False] * M for _ in range(N)]
    visited[0][0] = True

    cnt = 1000000

    di = [0, 1, 0, -1]
    dj = [1, 0, -1, 0]
    # 시작점 (0,0)
    dfs(0,0,1)

    print(f"#{tc} {cnt}")