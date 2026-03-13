import sys; sys.stdin = open("5176 이진탐색_input.txt")

def inorder(t):
    global num, N

    if t <= N:
        inorder(t * 2)  # 왼쪽
        tree[t] = num  # 현재노드의 값
        num += 1
        inorder(t * 2 + 1)  # 오른쪽
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    N = int(input())
    nums = list(range(1,N+1))
    tree = [0]*(N+1)
    num = 1
    inorder(1)
    # print(tree)
    print(f"#{testcase} {tree[1]} {tree[N//2]}")