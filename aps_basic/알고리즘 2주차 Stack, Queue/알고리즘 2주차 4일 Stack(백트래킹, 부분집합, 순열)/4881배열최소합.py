import sys; sys.stdin = open('4881배열최소합_input.txt')


# def backtrack(i, cur_sum):
#     global result
#
#     if cur_sum >= result:
#         return
#
#     if i == N: # 마지막 행까지 선택 완료하면
#         result = min(result, cur_sum)
#         return
#
#     for j in range(N):
#         if not path[j]: # 선택하지 않은 열
#             path[j] = 1
#             backtrack(i + 1, cur_sum + arr[i][j])
#             path[j] = 0
#
#
# t = int(input())
# for tc in range(1,t+1):
#     N = int(input())
#     arr = [list(map(int, input().split())) for _ in range(N)]
#     result = 1000000
#     path = [0]*N
#     backtrack(0,0)
#
#     print(f"#{tc} {result}")
# ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
# ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
# 강사님 풀이
def perm(i, now_sum):
    global result
    # 가지치기
    if now_sum >= result:
        return

    if i == N:
        print(path)
        print(result, now_sum)
        result = min(result, now_sum)
        return

    else:
        for j in range(i, N):
            path[i], path[j] = path[j], path[i]     # 자리교환
            perm(i + 1, now_sum + arr[i][path[i]])  # i+1 자리 결정
            path[i], path[j] = path[j], path[i]     # 원상복구


t = int(input())
for tc in range(1,t+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    result = 1000000
    path = [i for i in range(N)]    # P[i] : i 에서 고를 열 번호
    perm(0,0)

    print(f"#{tc} {result}")