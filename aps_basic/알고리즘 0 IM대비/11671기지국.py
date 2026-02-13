import sys; sys.stdin = open('11671기지국_input.txt')


def cover(i,j):
    pass
    house = 0
    for d in range(4):
        r,c = i,j





#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
t = int(input())
for tc in range(1,t+1):
    N = int(input())
    arr = [list(input()) for _ in range(N)]

    # 각 기지국 별 커버하는 셀 수
    SST = {'A':1, 'B':2, 'C':3}

    dr = [0,1,0,-1]
    dc = [1,0,-1,0]

    position = []

    for i in range(N):
        for j in range(N):
            if arr[i][j] in 'ABC':
                position.append((i,j))

