import sys
sys.stdin = open('1979어디에단어드감_input.txt')

t = int(input())
for tc in range(1, t+1):
    n, k = map(int, input().split())
    # n: 퍼즐 가로세로, k: 글자 크기

    result = 0

    board = []
    for i in range(n):
        row = list(map(int, input().split()))
        board.append(row)

        # 가로 체크
        cnt1 = 0
        for j in range(n):
            if row[j] == 1:
                cnt1 += 1
            else:
                if cnt1 == k:
                    result += 1

    # 세로 체크
    for i in range(n):
        cnt2 = 0
        for j in range(n):
            if board[j][i] == 1:
                cnt2 += 1
            else:
                if cnt2 == k:
                    result += 1

    print(f'#{tc} {result}')

