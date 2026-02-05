import sys
sys.stdin = open('1215회문1_input.txt')

for tc in range(1, 11):
    n = int(input())
    arr = [list(input().strip()) for _ in range(8)]

    cnt = 0
    for i in range(8):
        for j in range(8-n+1):
            # 가로
            if arr[i][j:j+n] == arr[i][j:j+n][::-1]:
                cnt += 1

            # 세로
            check = ''
            for k in range(j, j+n):
                check += arr[k][i]
            if check == check[::-1]:
                cnt += 1
    print(f'#{tc} {cnt}')