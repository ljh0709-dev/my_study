import sys; sys.stdin = open('1232 사칙연산_input.txt')


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


    for i in range(N,0,-1):
        if heap[i] == '-':
            heap[i] = (heap[left[i]] - heap[right[i]])
        elif heap[i] == '+':
            heap[i] = (heap[left[i]] + heap[right[i]])
        elif heap[i] == '*':
            heap[i] = (heap[left[i]] * heap[right[i]])
        elif heap[i] == '/':
            heap[i] = (heap[left[i]] / heap[right[i]])

    # print(f"left:", left)
    # print(f"right:", right)
    # print(heap)

    print(f"#{tc} {int(heap[1])}")



