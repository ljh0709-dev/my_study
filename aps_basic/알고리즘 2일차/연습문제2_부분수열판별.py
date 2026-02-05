import sys
sys.stdin = open('연습문제2_부분수열판별_input.txt')

t = int(input())
for tc in range(1, t+1):
    n, m = map(int, input().split())
    # n: 수열 A의 길이, m: 수열 B의 길이
    a = list(map(int, input().split()))
    b = list(map(int, input().split()))

    check = [0] * m
    idx = 0
    for i in a:
        if i == b[idx]:
            check[idx] = 1
            idx += 1
            if idx == m:
                break

    total = 0
    for i in check:
        total += i

    if total == m:
        print(f'#{tc} YES')
    else:
        print(f'#{tc} NO')

