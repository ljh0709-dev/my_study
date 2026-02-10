import sys
sys.stdin = open('22783도너츠_input.txt')

t = int(input())
for tc in range(1,t+1):
    N, M, K = map(int, input().split())
    arr = [list(map(int, input().split())) for _ in range(N)]

    