import sys
sys.stdin = open('연습문제3_대각선의합_input.txt')

t = int(input())
for tc in range(1,t+1):
    n = int(input())
    arr = [list(map(int, input().split())) for _ in range(n)]

    cross1 = cross2 = 0
    for i in range(n):
        cross1 += arr[i][i]
        cross2 += arr[i][n-1-i]

    result = cross1 + cross2 - arr[n//2][n//2]
    print(f'#{tc} {result}')