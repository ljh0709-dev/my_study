import sys; sys.stdin = open('4880토너먼트카드게임_input.txt')

# 토너
def tnmt(start, end):
    if start == end:
        return start

    mid = (start + end) // 2
    left = tnmt(start, mid)
    # print(f"left: ", left, end = ' ')
    right = tnmt(mid + 1, end)
    # print(f"right: ", right, end = ' ')
    return win(left, right)


# 승패 여부 판단 -> 이긴 애 반환
def win(i, j):
    if (cards[i] == 1 and cards[j] == 2) or \
        (cards[i] == 2 and cards[j] == 3) or \
        (cards[i] == 3 and cards[j] == 1):
        return j
    else:   # 같아도 번호 빠른 애가 이김
        return i

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
t = int(input())
for tc in range(1,t+1):
    N = int(input())
    cards = list(map(int, input().split()))


    winner = tnmt(0, N - 1) + 1
    print(f"#{tc} {winner}")