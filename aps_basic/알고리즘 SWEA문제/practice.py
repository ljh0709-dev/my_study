import sys
# input = sys.stdin.readline
sys.stdin = open('practice_input.txt')

t = int(input())
for tc in range(1,t+1):
    N, M = map(int, input().split())

    # n번만큼 반복해서 조사할건데 한번이라도 0 나오면 off
    for i in range(N):
        # m의 i번째 비트가 1인지 아닌지 검사
        print(M & 1<<i)
        if M & (1<<i) == 0:
            print(f"#{tc} OFF")
            break
    else:
        print(f"#{tc} ON")