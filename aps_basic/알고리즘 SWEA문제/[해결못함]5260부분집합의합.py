import sys
sys.stdin = open('[해결못함]5260부분집합의합_input.txt')


def subset(N, K):
    arr = [i for i in range(1,N+1)]

    cnt = 0

    for i in range(1, 1<<N):
        subset_sum = 0
        for j in range(N):
            if i & (1<<j):
                subset_sum += arr[j]
        if subset_sum == K:
            cnt += 1

    return cnt

########################################
t = int(input())
for tc in range(1, t+1):
    N, K = map(int, input().split())

    print(f'#{tc} {subset(N,K)}')
########################################
# 100 5050일때 시간 오래걸림