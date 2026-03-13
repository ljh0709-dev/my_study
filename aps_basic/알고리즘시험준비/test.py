import sys
sys.stdin = open('test_input.txt')


def solve(r, c):
    dr = [0,1,0,-1]
    dc = [1,0,-1,0]



    for d in range(4):
        tr, tc = r, c
        visited[tr][tc] = 1
        while True:
            nr = tr + dr[d]
            nc = tc + dc[d]
            if not(0<=nr<N and 0<=nc<N):
                break
            if arr[nr][nc] == 1:
                visited[nr][nc] = 1
                break
            tr = nr
            tc = nc
            visited[tr][tc] = 1

def find_start():
    start = []
    for r in range(N):
        for c in range(N):
            if arr[r][c] == 2:
                start.append([r,c])
    return start
####################
t = int(input())
for testcase in range(1,t+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    visited = [[0]*N for _ in range(N)]
    cnt = 0

    start = find_start()
    for r, c in start:
        solve(r,c)


    for r in range(N):
        for c in range(N):
            if arr[r][c]==1:
                visited[r][c] = 1
            if visited[r][c]==0:
                cnt += 1

    for i in visited:
        print(i)
    print(f"#{testcase} {cnt}")