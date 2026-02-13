import sys; sys.stdin = open('14912부분집합의합_input.txt')

# cur_sum: 고려한 원소의 합, t: 찾으려는 합
def f(i, N, cur_sum, t):
    global result

    if cur_sum > t:
        return
    elif cur_sum == t and set(path) != {0}:
        result = 1
        return
    elif i ==N:
        return
    else:
        path[i] = 1  # arr[level] 포함
        f(i + 1, N, cur_sum + arr[i], t)

        path[i] = 0  # arr[level] 미포함
        f(i + 1, N, cur_sum, t)


t = int(input())
for tc in range(1,t+1):
    N = int(input())
    arr = list(map(int, input().split()))
    path = [0]*N
    result = 0

    f(0,N,0,0)
    print(f"#{tc} {result}")
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
# 강사님 풀이
def powerset(i, now_sum):
    global result

    if i == N:
        # 합이 0인 경우 찾기
        if now_sum == 0 and sum(path) != 0:
            result = 1
            return
    else:
        path[i] = 1         #arr[i] 포함
        powerset(i + 1, now_sum + arr[i])
        path[i] = 0         #arr[i] 미포함
        powerset(i + 1, now_sum)


t = int(input())
for tc in range(1,t+1):
    N = int(input())
    arr = list(map(int, input().split()))
    path = [0]*N
    result = 0

    powerset(0,0)
    print(f"#{tc} {result}")