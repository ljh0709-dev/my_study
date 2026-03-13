import sys
sys.stdin = open('5097 회전.txt')
from collections import deque

T = int(input())
for _ in range(1,T+1):
    N, M = map(int, input().split())
    nums = list(map(int, input().split()))

    q = deque()
    for i in nums:
        q.append(i)

    while M > 0:
        pop_num = q.popleft()
        q.append(pop_num)
        M -= 1

    print(f'#{_} {q[0]}')
