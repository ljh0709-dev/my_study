import sys
sys.stdin = open('1209Sum_input.txt')

for _ in range(10):
    tc = int(input())
    arr = [list(map(int, input().split())) for _ in range(100)]

    # 행 합
    row_sum = 0
    for i in range(100):
        if row_sum < sum(arr[i]):
            row_sum = sum(arr[i])

    # 열 합
    col_sum = 0
    for i in range(100):
        col = 0
        for j in range(100):
            col += arr[j][i]
        if col_sum < col:
            col_sum = col

    # 대각, 역대각 합
    cross1 = cross2 = 0
    for i in range(100):
        cross1 += arr[i][i]
        cross2 += arr[i][100-i-1]

    print(f'#{tc} {max(row_sum, col_sum, cross1, cross2)}')


