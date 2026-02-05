import sys
sys.stdin = open('9490풍선팡_input.txt')

t = int(input())

for tc in range(1,t+1):
    n, m = map(int, input().split())
    arr = [list(map(int, input().split())) for _ in range(n)]

    # 우, 하, 좌, 상 순서
    di = [0, 1, 0, -1] # 행
    dj = [1, 0, -1, 0] # 열

    max_value = 0

    for i in range(n): # 행
        for j in range(m): # 열
            now = arr[i][j]
            for d in range(4):
                for flower in range(1, arr[i][j]+1):
                    next_i = i + di[d] * flower
                    next_j = j + dj[d] * flower
                    # 유효한 인덱스일 때
                    if 0 <= next_i < n and 0 <= next_j < m:
                        now += arr[next_i][next_j]

            if max_value < now:
                max_value = now

    print(f'#{tc} {max_value}')
