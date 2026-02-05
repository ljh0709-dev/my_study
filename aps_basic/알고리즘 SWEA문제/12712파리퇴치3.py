import sys
sys.stdin = open('12712파리퇴치_input.txt')

def spray(n, m, arr):
    # n: 배열 가로/세로 크기, m: 파리채 가로/세로 크기
    max_kill = 0

    # 우, 하, 좌, 상, (+)
    di = [0, 1, 0, -1]  # 행
    dj = [1, 0, -1, 0]  # 열
    # 우하, 좌하, 좌상, 우상 (x)
    di2 = [1, 1, -1, -1]  # 행
    dj2 = [1, -1, -1, 1]  # 열

    for i in range(n):
        for j in range(n):
            # + 에프킬라
            plus_kill = arr[i][j]
            for d in range(4):
                for k in range(1,m):  # 가운데 칸 포함 m 칸
                    next_i = i + di[d] * k
                    next_j = j + dj[d] * k
                    if 0 <= next_i < n and 0 <= next_j < n:
                        plus_kill += arr[next_i][next_j]

            # x 에프킬라
            x_kill = arr[i][j]
            for d in range(4):
                for k in range(1,m):  # 가운데 칸 포함 m 칸
                    next_i = i + di2[d] * k
                    next_j = j + dj2[d] * k
                    if 0 <= next_i < n and 0 <= next_j < n:
                        x_kill += arr[next_i][next_j]

            max_kill = max(max_kill, plus_kill, x_kill)

    return max_kill


t = int(input())

for tc in range(1,t+1):
    n, m = map(int, input().split())
    arr = [list(map(int, input().split())) for _ in range(n)]

    print(f"#{tc} {spray(n,m,arr)}")