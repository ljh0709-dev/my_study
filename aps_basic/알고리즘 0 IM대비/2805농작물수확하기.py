import sys
sys.stdin = open('2805농작물수확하기_input.txt')

t = int(input())
for tc in range(1,t+1):
    n = int(input())
    arr = [list(map(int, input())) for _ in range(n)]

    coin = 0
    for i in range(n):
        point = n//2
        if i <= point:
            upper_area = arr[i][point-i:point+i+1]
            print(f"upper: {upper_area}")
        else:
            lower_area = arr[i][n-point:n-point+1]
            print(f"lower: {lower_area}")