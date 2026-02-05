import sys
sys.stdin = open('1210Ladder1_input.txt')


for _ in range(10):
    tc = int(input())
    arr = [list(map(int, input().split())) for _ in range(100)][::-1]
    # 행 전체 뒤집어서 내려오기
    ########################################
    i = 0 # 행
    j = 0 # 열
    for idx in range(100):  # 시작 열 찾기
        if arr[0][idx] == 2:
            j = idx
            break
    ########################################
    while i < 100:
        # 1. 왼쪽에 길이 있다면, 끝까지 왼쪽으로
        if j > 0 and arr[i][j-1] == 1:
            while j > 0 and arr[i][j-1] == 1:
                j -= 1

        # 2. 오른쪽에 길이 있다면, 끝까지 오른쪽으로
        elif j < 99 and arr[i][j+1] == 1:
            while j < 99 and arr[i][j+1] == 1:
                j += 1

        # 3. 좌우에 길 없으면 아래로 한 칸
        i += 1
    ########################################
    print(f'#{tc} {j}')
