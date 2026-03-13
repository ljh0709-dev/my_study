import sys; sys.stdin = open("4963 섬의 개수_input.txt")

def solve(r,c):
    global island
    s = [[r,c]]

    while s:
        r, c = s.pop()
        if arr[r][c] == 1:
            island += 1

        for dr, dc in [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < h and 0 <= nc < w and\
                    visited[nr][nc] == 0 and arr[nr][nc] == 1:
                arr[nr][nc] = 0
                s.append([nr,nc])


while True:
    w, h = map(int, input().split())
    if w == 0 and h == 0:
        break

    arr = [list(map(int, input().split())) for _ in range(h)]
    # 1: 땅, 0: 바다

    visited = [[0]*w for _ in range(h)]

    island = 0
    for i in range(h):
        for j in range(w):
            if arr[i][j] == 1:
                solve(i, j)

    print(island)