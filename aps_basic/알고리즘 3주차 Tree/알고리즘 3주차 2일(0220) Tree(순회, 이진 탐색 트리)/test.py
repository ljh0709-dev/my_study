import sys; sys.stdin = open('1232_사칙연산.txt')

t = int(input())
for tc in range(1, t+1):
    N = int(input())
    left = [0]*(N+1)
    right = [0]*(N+1)
    par = [0]*(N+1)

    for _ in range(N):
        info = list(map(str, input().split()))
        if len(info)==4:    # 정점이 연산자
            par[int(info[0])] = info[1]
            left[int(info[0])] = int(info[2])
            right[int(info[0])] = int(info[3])
        else:   # 정점 정수
            par[int(info[0])] = int(info[1])

    for i in range(N,0,-1):
        if par[i] == '-':
            par[i] = (par[left[i]] - par[right[i]])
        elif par[i] == '+':
            par[i] = (par[left[i]] + par[right[i]])
        elif par[i] == '*':
            par[i] = (par[left[i]] * par[right[i]])
        elif par[i] == '/':
            par[i] = (par[left[i]] / par[right[i]])

    print(int(par[1]))

