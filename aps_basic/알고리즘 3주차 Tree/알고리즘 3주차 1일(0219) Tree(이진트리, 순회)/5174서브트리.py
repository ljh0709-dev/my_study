import sys; sys.stdin = open("5174서브트리_input.txt")


def pre_order(T):   # 전위순회, 방문한 정점(부모) 먼저 처리
    global cnt
    if T:   # 0이 아니면 (존재하는 정점이면)
        cnt += 1
        # print(T)    # visit(T) T에서 할일 처리
        pre_order(c1[T])  # 왼쪽 자식(서브트리)로 이동
        pre_order(c2[T])  # 오른쪽 자식(서브트리)로 이동


t = int(input())
for tc in range(1,t+1):
    # E: 간선 수, N: 노드
    E, N = map(int, input().split())
    arr = list(map(int, input().split()))

    V = E + 1       # 마지막 정점 번호 (간선 수 보다 1 큼)
    # 부모 번호를 인덱스로 자식 번호를 저장하는 배열!
    c1 = [0] * (V+1)
    c2 = [0] * (V+1)

    # 자식 번호를 인덱스로 자식 번호를 저장하는 배열
    parents = [0]  * (V+1)

    cnt = 0

    for i in range(E):
        p, c = arr[2*i], arr[2*i + 1]
        if c1[p] == 0:      # 아직 자식1이 없을 경우
            c1[p] = c
        else:
            c2[p] = c
        parents[c] = p      # 자식을 인덱스로 부모 저장


    # c = V
    # while parents[c] != 0:
    #     c = parents[c]
    # root = c


    # print(c1)
    # print(c2)
    # print(parents)

    pre_order(N)
    print(f"#{tc} {cnt}")
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
# 강사님 풀이
# def postorder(T):
#     if T == 0:
#         return 0
#     l = postorder(left[T])
#     r = postorder(right[T])
#     return l + r + 1
#
# T = int(input())
# for tc in range(1, T+1):
#     E, N = map(int, input().split())
#     arr = list(map(int, input().split()))
#
#     V = E + 1   # 정점 개수 = 간선 수 + 1
#
#     left = [0] * (V + 1)
#     right = [0] * (V + 1)
#     for i in range(E):
#         p, c = arr[i * 2], arr[i * 2 + 1]
#         if left[p] == 0:
#             left[p] = c
#         else:
#             right[p] = c
#     cnt = postorder(N)
#     print(f'#{tc} {cnt}')

