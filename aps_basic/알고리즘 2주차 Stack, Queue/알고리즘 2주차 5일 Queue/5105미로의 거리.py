import sys; sys.stdin = open('5105미로의 거리_input.txt')

def bfs(i, j, N):
    # 준비 = 인큐 + 방문체크
    visited = [[0]*N for _ in range(N)] # visited 생성
    q = []              # 큐 생성
    q.append([i,j])     # 시작점 인큐
    visited[i][j] = 1   # 시작점 인큐 표시
    # 탐색
    while q:
        ti, tj = q.pop(0)   # 디큐 + 할 일
        if maze[ti][tj] == 3:   # visit(t) 도착하면
            return visited[ti][tj] - 1 - 1 # 경로의 빈칸 수, -1 추가
        # 인접정점 w 미방문이면 인큐 + 방문체크
        for di, dj in [[0,1],[1,0],[0,-1],[-1,0]]: # 미로내부고, 인접이고 벽이아니면,
            wi, wj = ti+di, tj+dj
            if 0<=wi<N and 0<=wj<N and maze[wi][wj] != 1 and visited[wi][wj] == 0:
                q.append([wi, wj])  # 인큐
                visited[wi][wj] = visited[ti][tj] + 1   # 인큐 표시
    return 0


t = int(input())
for tc in range(1,t+1):
    N = int(input())
    maze = [list(map(int, input())) for _ in range(N)]

    sti, stj = 0, 0
    for i in range(N):
        for j in range(N):
            if maze[i][j] == 2:
                sti, stj = i, j
                break
        if sti and stj:
            break


    ans = bfs(sti, stj, N)
    print(f"#{tc} {ans}")
