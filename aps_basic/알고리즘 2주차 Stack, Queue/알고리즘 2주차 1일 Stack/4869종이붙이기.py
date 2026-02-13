import sys
sys.stdin = open('4869종이붙이기_input.txt')


def paper(n):
    # 교실 바닥 크기 = 20 * N
    # 1번종이 = 20*10, 2번종이 = 20*20
    cnt = 0

    for i in range(n//20, -1, -1):
        btn = n - i
        for j in range(1, btn//10 + 1):






t = int(input())
for tc in range(1,t+1):
    n = int(input())

