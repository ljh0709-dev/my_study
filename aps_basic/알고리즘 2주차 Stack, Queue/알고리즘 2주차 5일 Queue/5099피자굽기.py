import sys; sys.stdin = open('5099피자굽기_input.txt')


def solve(arr):
    # 화덕에 N개의 피자 넣기
    q = []
    for i in range(N):
        q.append(i)

    idx = N  # 마지막에 넣는 피자 번호
    while len(q) > 1:
        # 피자 꺼내서 치즈 확인
        cheese = q.pop(0)
        arr[cheese] //= 2

        # 치즈 남았으면 다시 넣기
        if pizza[cheese] != 0:
            q.append(cheese)
        # 치즈가 다 녹았으면 남은 피자 넣기
        elif idx < M:
            q.append(idx)
            idx += 1
    return q.pop()


# 강사님 풀이
t = int(input())
for tc in range(1,t+1):
    N, M = map(int, input().split())
    pizza = list(map(int, input().split()))

    print(f"#{tc} {solve(pizza) + 1}")
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
# t = int(input())
# for tc in range(1, t + 1):
#     N, M = map(int, input().split())
#     pizza = list(map(int, input().split()))
#
#     cheese = []
#     for i in range(M):
#         cheese.append([i + 1, pizza[i]])
#
#     oven = cheese[:N]  # 화덕에 넣을 피자
#     remain = cheese[N:]  # 남은 피자
#
#     while len(oven) > 1:
#         check = oven.pop(0)
#         check[1] //= 2  # 치즈 녹음
#         if check[1] == 0:  # 치즈 다 녹았으면
#             if remain:  # 남은 피자 있으면
#                 oven.append(remain.pop(0))
#         else:  # 치즈 덜 녹았으면 다시 넣음
#             oven.append(check)
#
#     print(f"#{tc} {oven[0][0]}")