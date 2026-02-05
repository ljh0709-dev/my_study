import sys
sys.stdin = open('4836색칠하기_input.txt')

t = int(input())

for tc in range(1, t+1):
    n = int(input())
    # r1, c1, r2, c2, color 순서
    paper = [list(map(int, input().split())) for _ in range(n)]
    # 왼쪽 위 (r1, c1), 오른쪽 아래 (r2, c2)
    # color 1 : 빨강, 2 : 파랑

    arr = [[0] * 10 for _ in range(10)]

    for i in paper:
        for x in range(i[0], i[2]+1):
            for y in range(i[1], i[3]+1):
                if arr[x][y]:
                    arr[x][y] = 7
                else:
                    arr[x][y] = i[4]

    pupple = 0
    for i in range(10):
        for j in arr[i]:
            if j == 7:
                pupple += 1

    print(f'#{tc} {pupple}')