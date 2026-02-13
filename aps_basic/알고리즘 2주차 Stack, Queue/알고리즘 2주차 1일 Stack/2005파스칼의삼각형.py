import sys
sys.stdin = open('2005파스칼의삼각형_input.txt')


t = int(input())
for tc in range(1,t+1):
    n = int(input())

    arr = [[0] * n for _ in range(n)]

    for i in range(n):
        arr[i][0] = 1
        arr[i][i] = 1

    for i in range(2,n):
        for j in range(1,n):
            arr[i][j] = arr[i-1][j-1] + arr[i-1][j]


    print(f"#{tc}")
    for i in range(n):
        print(*arr[i][:i+1])