import sys
sys.stdin = open('22783도너츠_input.txt')

t = int(input())
for tc in range(1, t + 1):
    N, M, K = map(int, input().split())
    arr = [list(map(int, input().split())) for _ in range(N)]

    fish = 0

    for i in range(N - K + 1):
        for j in range(N - K + 1):
            net = 0
            for r in range(i, i + K):
                if r == i:
                    net += sum(arr[r][j:j + K])
                elif r == i + K - 1:
                    net += sum(arr[r][j:j + K])
                else:
                    net += (arr[r][j] + arr[r][j + K - 1])

            if fish < net:
                fish = net
    print(f"#{tc} {fish}")