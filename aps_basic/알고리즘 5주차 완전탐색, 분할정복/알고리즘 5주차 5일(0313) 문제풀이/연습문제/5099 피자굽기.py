import sys
sys.stdin = open('5099 피자굽기.txt')
from collections import deque

T = int(input())
for _ in range(1,T+1):
    N, M = map(int, input().split())
    pizza = list(map(int, input().split()))

    cheese = []
    for i in range(M):
        cheese.append([i+1, pizza[i]])

    oven = deque(cheese[:N])
    remain = deque(cheese[N:])

    while len(oven) > 1:
        check = oven.popleft()
        check[1] //= 2  # 치즈 녹임
        if check[1] == 0:
            if remain:
                oven.append(remain.popleft())
        else:
            oven.append(check)


    print(f'#{_} {oven[0][0]}')
