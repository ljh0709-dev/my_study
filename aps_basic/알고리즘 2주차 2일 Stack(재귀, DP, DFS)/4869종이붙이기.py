import sys; sys.stdin = open('4869종이붙이기_input.txt')


def solve(N):
    dp = [0] * (N+1)
    dp[0] = 1
    dp[1] = 1
    # F(0) = 1  안만드는 경우
    # F(1) = 1  a 1장
    # F(2) = 3  a 2장 │ b 1장 │ c 2장
    # F(3) = 5  a 3장 │ a 1장 b 1장 * 2 │ a 1장 c 2장 * 2
    # F(4) = 11  a 4장 │ a 2장 b 1장 * 3 │ a 2장 c 2장 * 3 │ b 2장 │ c 4장 │ b 1장 c 2장 * 2
    # F(N) = F(N-1) + 2 * F(N-2)

    for i in range(2, N + 1):
        dp[i] = dp[i-1] + 2 * dp[i-2]

    return dp[N]

##############################
t = int(input())
for tc in range(1,t+1):
    N = int(input())
    # 종이a: 20*10, 종이b: 20*20, 종이c: 10*20
    N //= 10

    print(f"#{tc} {solve(N)}")
