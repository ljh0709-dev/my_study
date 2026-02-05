import sys
sys.stdin = open('연습문제3_4방향연습_input.txt')

def my_ads(n):
    if n < 0:
        return n * (-1)
    else:
        return n


T = int(input())

for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int,input().split())) for _ in range(N)]

    # 우, 하, 좌, 상 순서
    di = [0, 1, 0, -1] # 행
    dj = [1, 0, -1, 0] # 열

    total = 0

    for i in range(N):
        for j in range(N):
            s = 0
            for d in range(4):
                next_i = i + di[d]
                next_j = j + dj[d]
                if 0 <= next_i < N and 0 <= next_j < N:
                    s += my_ads(arr[i][j] - arr[next_i][next_j])
            total += s
    print(f'#{tc} {total}')