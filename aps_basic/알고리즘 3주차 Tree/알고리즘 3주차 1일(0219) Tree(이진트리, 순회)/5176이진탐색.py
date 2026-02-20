# 완전 이진 트리, 중위순회로 ㄱ
import sys;sys.stdin = open("5176이진탐색_input.txt")


def inorder(t):
    global root, N

    if t <= N:
        inorder(t * 2)  # 왼쪽
        tree[t] = root  # 현재
        root += 1
        inorder(t * 2 + 1)  # 오른쪽


t = int(input())
for tc in range(1,t+1):
    N = int(input())

    tree = [0] * (N + 1)

    root = 1
    inorder(1)

    #print(tree[1:])
    print(f"#{tc}", tree[1], tree[N//2])

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
# # 강사님 풀이
# def solve(v):
#     global num, N
#
#     if v <= N:
#         solve(2*v)
#         tree[v] = num
#         num += 1
#         solve((2*v + 1))
#
#
# T = int(input())
# for tc in range(1, T+1):
#     N = int(input())
#
#     tree = [0] * (N + 1)    # 완전이진트리를 저장할 배열
#
#     num = 1               # 입력할 번호
#     solve(1)              # 완전이진트리의 루트는 1
#
#     print(f'#{tc} {tree[1]} {tree[N//2]}')
