import sys; sys.stdin = open("1247 최적경로_input.txt")

t = int(input())
for testcase in range(1,t+1):
    N = int(input())
    arr = [[0]*101 for _ in range(101)]
    pos = list(map(int, input().split()))
    arr[pos[0]][pos[1]] = 'c'   # 회사
    arr[pos[2]][pos[3]] = 'h'   # 집

    pos = pos[4:]
    for i in range(len(pos)//2):
        arr[pos[2*i]][pos[2*i+1]] = 'p'
    #ㅡㅡㅡㅡㅡㅡarr 표시 완료ㅡㅡㅡㅡㅡㅡ




