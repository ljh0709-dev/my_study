import sys; sys.stdin = open("5201 컨테이너 운반_input(greedy).txt")


T = int(input())
for testcase in range(1,T+1):
    # N: 컨테이너 수, M: 트럭 수
    N, M = map(int, input().split())
    # N개의 컨테이너 무게
    containers = sorted(list(map(int, input().split())), reverse=True)
    check = [0] * N
    # M개 트럭의 적재 용량
    trucks = sorted(list(map(int, input().split())), reverse=True)
    total = 0


    # 트럭 기준으로 체크
    for i in range(M):
        # 트럭이 모든 컨테이너를 옮긴 경우 종료
        if i == N:
            break

        # i 번째 트럭 기준으로 옮길 수 있는 컨테이너 체크
        for j in range(i, N):
            # 이미 옮긴 컨테이너면 패스
            if check[j]:
                continue

            # 트력 적재용량이 컨테이너 무게 이상이면 옮길 수 있음
            if trucks[i] >= containers[j]:
                total += containers[j]
                check[j] = 1    # 옮긴 컨테이너 표시
                break           # 다음 트럭 체크

    # print(check)
    # print(containers)
    # print(trucks)
    print(f"#{testcase} {total}")

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# 강사님 코드
T = int(input())
for testcase in range(1,T+1):
    # N: 컨테이너 수, M: 트럭 수
    N, M = map(int, input().split())
    # N개의 컨테이너 무게
    containers = sorted(list(map(int, input().split())), reverse=True)
    # M개 트럭의 적재 용량
    trucks = sorted(list(map(int, input().split())), reverse=True)


    i = j = ans = 0     # i: 컨테이너 인덱스, j: 트럭 인덱스
    while i < N and j < M:
        # 트럭으로 옮길 수 있을 때
        if containers[i] <= trucks[j]:
            ans += containers[i]
            i += 1
            j += 1
        else:   # 옮길 수 없는 경우 : 다음 컨테이너 체크
            i += 1
    print(f"#{testcase} {ans}")
