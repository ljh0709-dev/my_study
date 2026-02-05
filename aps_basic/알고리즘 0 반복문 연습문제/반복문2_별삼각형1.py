import sys
sys.stdin = open('반복문2_별삼각형1_input.txt')

t = int(input())
for tc in range(1, t+1):
    n, m = map(int, input().split())
    print(f'#{tc}')
    for i in range(1,n+1):
        if m == 1:
            s = '*' * i
            print(s)
        elif m == 2:
            s = '*' * (n+1-i)
            print(s)
        else:
            s = ' ' * (n-i) + '*' * (2*i - 1) + ' ' * (n-i)
            print(s)
