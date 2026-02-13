import sys; sys.stdin = open('20454동전거스름돈_input.txt')

t = int(input())
for tc in range(1,t+1):
    m = int(input())    # 거스름돈
    n = int(input())    # 동전 종류 수
    coins = sorted(list(map(int, input().split())), reverse=True)

    dp = [float('inf')] * (m+1)
    dp[0] = 0

    for coin in coins:
        for money in range(coin, m + 1):
            dp[money] = min(dp[money], dp[money - coin] + 1)


    print(f"#{tc} {cnt}")
