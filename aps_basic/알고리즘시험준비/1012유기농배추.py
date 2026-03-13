import sys; sys.stdin = open("1012유기농배추_input.txt")


def dfs(r,c):
    s = [[r,c]]
    while s:
        r,c = s.pop()
        for dr, dc in [[0,1], [1,0], [0,-1], [-1,0]]:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < N and 0 <= nc < M and arr[nr][nc] == 1:
                arr[nr][nc] = 0
                s.append([nr,nc])

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
T = int(input())
for _ in range(T):
    M, N, K = list(map(int, input().split()))
    # M: 배추밭 가로, N: 배추밭 세로, K: 배추 개수
    arr = [[0]*M for _ in range(N)]

    # 배추 위치
    for _ in range(K):
        x, y = map(int, input().split())
        arr[y][x] = 1


    cnt = 0
    for i in range(N):
        for j in range(M):
            if arr[i][j] == 1:
                dfs(i, j)
                cnt += 1

    print(cnt)