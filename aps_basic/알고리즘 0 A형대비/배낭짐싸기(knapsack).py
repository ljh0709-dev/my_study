import sys; sys.stdin = open('배낭짐싸기(knapsack)_input.txt')

T = int(input())
for testcase in range(1,T+1):
    # N: 물건 수, K: 가방 용량
    N, K = map(int, input().split())
    products = [list(map(int, input().split())) for _  in range(N)]

    dp = [0] * (K+1)
    for w, v in products:
        for k in range(K,w-1,-1):
            dp[k] = max(dp[k], dp[k-w] + v)

    print(f"#{testcase} {max(dp[:K+1])}")