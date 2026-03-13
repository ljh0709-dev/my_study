import sys; sys.stdin = open('5207 이진탐색(분할정복)_input.txt')

def binary_search(target):
    l = 0        # start
    r = N - 1   # end
    direct = 0

    while l <= r:   # 교차되는 순간은 target 못찾은 경우
        mid = (l+r) // 2

        # 목표 찾으면 종료
        if A[mid] == target:
            return mid

        # target < A[mid] 인 경우: target은 mid 왼쪽에 위치
        # mid 기준 왼쪽 체크
        if target < A[mid]:
            if direct == 1:
                return -1
            r = mid - 1
            direct = 1

        # A[mid] < target 인 경우: target은 mid 오른쪽에 위치
        # mid 기준 오른쪽 체크
        else:
            if direct == 2:
                return -1
            l = mid + 1
            direct = 2

    return -1

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    N, M = map(int, input().split())
    A = sorted(list(map(int, input().split())))
    B = list(map(int, input().split()))

    # Target이 A에 들어있으면서, 연속으로 같은 방향 아니면 cnt +1
    cnt = 0

    for target in B:
        answer = binary_search(target)
        if answer != -1:
            cnt += 1

    print(f"#{testcase} {cnt}")