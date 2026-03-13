import sys; sys.stdin = open('5188 최소합(완전탐색)_input.txt')

dr = [1,1,-1,-1]
dc = [1,-1,1,-1]

def solve(r, c, direct ,total):
    global max_dessert
    # 다음 방향을 먼저 설정 (도착지로 돌아와야 하기 때문)
    nr = r + dr[direct]
    nc = c + dc[direct]

    # 출발점에 도착하면
    if r == start_r and c == start_c:
        max_dessert = max(max_dessert, total + 1)
        return

    # 인덱스, 방문 체크
    if 0<=nr<N and 0<=nc<N and dessert[arr[nr][nc]]==0:
        dessert[arr[nr][nc]] = 1
        # 직진
        solve(nr, nc, direct, total + 1)
        # 방향전환
        if direct < 3:  # 마지막 방향 전환 안됨
            solve(nr, nc, direct+1, total + 1)
        dessert[arr[nr][nc]] = 0
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
t = int(input())
for testcase in range(1,t+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    dessert = [0]*101
    max_dessert = -1

    for r in range(N):
        for c in range(1,N-1):
            start_r, start_c = r,c
            dessert[arr[r][c]] = 1
            solve(r+1, c+1, 0, 1)
            dessert[arr[r][c]] = 0

    print(f"#{testcase} {max_dessert}")