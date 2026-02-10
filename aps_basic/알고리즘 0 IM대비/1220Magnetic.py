import sys
sys.stdin = open('1220Magnetic_input.txt')


for tc in range(1,11):
    n = int(input())
    arr = [list(map(int, input().split())) for _ in range(n)]
    # 1: N극(아래로), 2: S극(위로)

