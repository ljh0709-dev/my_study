# 완전 이진 트리 -> 1차원 배열로 저장 후 활용 ㄱ
import sys;sys.stdin = open("1231중위순회_input.txt")


def inorder(t):  # 중위순회, 방문한 정점(부모) 먼저 처리
    global answer

    if t:   # 0이 아니면 (존재하는 정점이면)
        inorder(left[t])  # 왼쪽 자식(서브트리)로 이동
        #print(t, end = ' ')    # visit(T) T에서 할일 처리
        answer += words[t]
        inorder(right[t])  # 오른쪽 자식(서브트리)로 이동


for tc in range(1,11):
    N = int(input())    # 정점 수
    E = N - 1           # 간선 수

    left = [0] * (N+1)  # 부모번호를 인덱스로 왼쪽 자식 저장 배열
    right = [0] * (N+1)  # 부모번호를 인덱스로 오른쪽 자식 저장 배열
    parent = [0] * (N+1)  # 자식 번호를 인덱스로 부모 번호 저장 배열

    words = {}
    for _ in range(N):
        info = list(input().split())
        words[int(info[0])] = info[1]

        if len(info) == 4:
            left[int(info[0])] = int(info[2])
            right[int(info[0])] = int(info[3])
            parent[int(info[2])] = int(info[0])
            parent[int(info[3])] = int(info[0])
        elif len(info) == 3:
            left[int(info[0])] = int(info[2])
            parent[int(info[2])] = int(info[0])

    #print(words)
    #print(left[1:])
    #print(right[1:])
    #print(parent[1:])

    root = 0
    for i in range(1,N+1):
        if parent[i] == 0:  # 부모 없으면 root
            root = i
            break

    answer = ''

    inorder(root)
    print(f"#{tc} {answer}")

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
# # 강사님 풀이
# def inorder(v):
#     global answer
#
#     if v <= N:
#         inorder(2*v)
#         answer += tree[v]
#         inorder(2*v+1)
#
#
# for tc in range(1,11):
#     N = int(input())
#
#     tree = [0] * (N+1)
#     for _ in range(N):
#         info = list(input().split())
#         idx = int(info[0])
#         tree[idx] = info[1]
#
#     answer = ''
#     inorder(1)
#     print(f"#{tc} {answer}")

