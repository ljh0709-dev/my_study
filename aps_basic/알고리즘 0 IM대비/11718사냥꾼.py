import sys; sys.stdin = open('11718사냥꾼_input.txt')


def kill(i,j):
    rabbit = 0

    for d in range(8):
        r, c = i, j     # 사냥꾼 초기 위치

        while True:
            nr = r + dr[d]
            nc = c + dc[d]
            if not(0 <= nr < N and 0 <= nc < N):
                break
            if arr[nr][nc] == 3:
                break
            if arr[nr][nc] == 2:
                rabbit += 1

            r, c = nr, nc

    return rabbit
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
t = int(input())
for tc in range(1,t+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    # 0: 빈 공간, 1: 사냥꾼, 2: 토끼, 3: 바위를 의미

    # 우, 하, 좌, 상, 우하, 좌하, 좌상, 우상
    dr = [0, 1, 0, -1, 1, 1, -1, -1]
    dc = [1, 0, -1, 0, 1, -1, -1, 1]

    hunt = []
    for i in range(N):
        for j in range(N):
            if arr[i][j] == 1:
                hunt.append((i,j))

    total = 0
    for i,j in hunt:
        total += kill(i,j)
    print(f"#{tc} {total}")