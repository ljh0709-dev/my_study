import sys
sys.stdin = open('반복문1_숫자사각형4_input.txt')

t = int(input())
for tc in range(1,t+1):
    n = int(input())

    arr = [[0]*n for  _ in range(n)]
    nums = [i for i in range(1,n+1)]

    for i in range(1,n+1):
        row = [i*j for j in nums]
        arr[i-1] = row

    print(f'#{tc}')
    for i in arr:
        print(*i)