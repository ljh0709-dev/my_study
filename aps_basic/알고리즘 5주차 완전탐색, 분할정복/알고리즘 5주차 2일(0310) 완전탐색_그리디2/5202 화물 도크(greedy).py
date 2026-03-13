import sys; sys.stdin = open("5202 화물 도크_input(greedy).txt")

T = int(input())
for testcase in range(1,T+1):
    N = int(input())
    trucks = sorted([list(map(int, input().split())) for _ in range(N)],
                    key=lambda x:(x[1], x[0]))

    # for i in trucks:
    #     print(i)

    # 가장 먼저 끝나는 트럭 선택 trucks[0], total = 1
    total = 1
    end = trucks[0][1]  # 첫 트럭 종료 시간

    # 다음 트럭은 이전 트럭 종료시간 이후에 시작하는 녀석들 중, 가장 빨리 끝나는 트럭
    for i in range(1,N):
        s, e = trucks[i]
        if end <= s:
            total += 1
            end = e

    print(f"#{testcase} {total}")
