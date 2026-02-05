import sys
sys.stdin = open('1979어디에단어가들어갈수있을까_input.txt')

def my_sum(n):
    total = 0
    for i in n:
        total += i
    return total


t = int(input())
for tc in range(1,t+1):
    n, k = map(int, input().split())
    # n: 가로,세로 길이, k: 단어의 길이
    # 흰색 1, 검은색 0
    arr = [list(map(int, input().split())) for _ in range(n)]

    total = 0
    # 가로 체크
    for row in arr:
        cnt = 0
        for i in range(n):
            if row[i] == 1:
                cnt += 1
            else:
                if cnt == k:
                    total += 1
                cnt = 0

        if cnt == k:
            total += 1


    # 세로 체크
    # 전치행렬 돌려서 가로로 체크
    for i in range(n):
        for j in range(i + 1, n):
            arr[i][j], arr[j][i] = arr[j][i], arr[i][j]

    for row in arr:
        cnt = 0
        for i in range(n):
            if row[i] == 1:
                cnt += 1
            else:
                if cnt == k:
                    total += 1
                cnt = 0

        if cnt == k:
            total += 1

    print(f'#{tc} {total}')
