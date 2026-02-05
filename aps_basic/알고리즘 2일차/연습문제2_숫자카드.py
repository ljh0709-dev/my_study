import sys
sys.stdin = open('연습문제2_숫자카드_input.txt')

t = int(input())

for tc in range(1, t+1):
    n = int(input())
    a = list(input().strip())

    cards = [0] * 10
    for i in a:
        cards[int(i)] += 1

    max_idx = 0
    max_num = cards[0]
    for i in range(10):
        if max_num <= cards[i]:
            max_idx = i
            max_num = cards[i]


    print(f'#{tc} {max_idx} {max_num}')