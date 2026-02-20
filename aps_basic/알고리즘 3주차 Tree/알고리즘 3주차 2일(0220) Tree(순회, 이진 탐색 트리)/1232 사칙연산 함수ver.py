import sys; sys.stdin = open('1232 사칙연산_input.txt')


def postorder(v):  # 후위순회, 방문한 정점(부모) 먼저 처리
    global N

    if v:   # 0이 아니면 (존재하는 정점이면)
        postorder(left[v])  # 왼쪽 자식(서브트리)로 이동
        postorder(right[v])  # 오른쪽 자식(서브트리)로 이동

        if heap[v] == '-':
            heap[v] = (heap[left[v]] - heap[right[v]])
        elif heap[v] == '+':
            heap[v] = (heap[left[v]] + heap[right[v]])
        elif heap[v] == '*':
            heap[v] = (heap[left[v]] * heap[right[v]])
        elif heap[v] == '/':
            heap[v] = (heap[left[v]] / heap[right[v]])


# t = int(input())
# for tc in range(1,t+1):
for tc in range(1,11):
    N = int(input())

    left = [0] * (N+1)
    right = [0] * (N+1)
    heap = [0] * (N+1)

    for _ in range(N):
        info = list(input().split())
        if len(info) == 2:  # 정점이 정수면
            heap[int(info[0])] = int(info[1])
        elif len(info) == 4:    # 정점이 연산자면
            heap[int(info[0])] = info[1]
            left[int(info[0])] = int(info[2])
            right[int(info[0])] = int(info[3])

    # print(f"left:", left)
    # print(f"right:", right)
    # print(heap)

    postorder(1)

    print(f"#{tc} {int(heap[1])}")