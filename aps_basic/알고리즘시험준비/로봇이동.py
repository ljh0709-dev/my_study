import sys
sys.stdin = open('test_input.txt')

N = int(input())
arr = [list(input().strip()) for _ in range(N)]

di = [0,1,0,-1] # row
dj = [1,0,-1,0] # col

# 로봇 위치 찾기
catch = False
for i in range(N):
    for j in range(N):
        if arr[i][j] == '#':
            rob_i, rob_j = i, j
            catch = True
            break
    if catch:
        break

visit = [[False]*N for _ in range(N)]
