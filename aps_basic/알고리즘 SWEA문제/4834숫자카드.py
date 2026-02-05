import sys
sys.stdin = open('4834숫자카드_input.txt')

t = int(input())

for tc in range(1, t+1):
    n = int(input())
    cnt = [0] * 10
    cards = list(input().strip())

    for i in cards:
        cnt[int(i)] += 1

    max_idx = 0
    for idx in range(10):
        if cnt[idx] >= cnt[max_idx]:
            max_idx = idx

    print(f'#{tc} {max_idx} {cnt[max_idx]}')