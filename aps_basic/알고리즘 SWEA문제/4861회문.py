import sys
sys.stdin = open('4861회문_input.txt')

t = int(input())
for tc in range(1,t+1):
    n, m = map(int, input().split())
    # m: 찾을 회문 길이
    arr = [list(input().strip()) for _ in range(n)]

    answer = []
    # 가로
    for i in range(0,n-m+1):
