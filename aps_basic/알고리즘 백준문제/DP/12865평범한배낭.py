import sys
sys.stdin = open("12865_input.txt")
# input = sys.stdin.readline

N, K = map(int, input().split())
info = [list(map(int, input().split())) for _ in range(N)]

dp = [0]*(K+1)

for w, v in info:
    for i in range(K, w-1, -1):
        dp[i] = max(dp[i], dp[i-w] + v)
        print(dp)

print(dp)
