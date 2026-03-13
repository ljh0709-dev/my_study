import sys; sys.stdin = open('1233사칙연산 유효성 검사_input.txt')
# 완전 이진트리

# t = int(input())
# for tc in range(1,t+1):
for tc in range(1,11):
    N = int(input())

    left = [0] * (N+1)
    right = [0] * (N+1)
    heap = [0] * (N+1)

    for _ in range(N):
        info = list(input().split())
        if len(info) == 2:
            if info[1].isdigit():  # 정점이 정수면
                heap[int(info[0])] = int(info[1])
            else:                  # 정점이 연산자면
                heap[int(info[0])] = info[1]
        elif len(info) == 4:    # 정점이 연산자면
            heap[int(info[0])] = info[1]
            left[int(info[0])] = int(info[2])
            right[int(info[0])] = int(info[3])

    # print(left)
    # print(right)
    # print(heap)
    # print()

    answer = 0
    for i in range(N,0,-1):
        if heap[i] == '-':
            heap[i] = (heap[left[i]] - heap[right[i]])
        elif heap[i] == '+':
            heap[i] = (heap[left[i]] + heap[right[i]])
        elif heap[i] == '*':
            heap[i] = (heap[left[i]] * heap[right[i]])
        elif heap[i] == '/':
            if heap[right[i]] == 0:
                break
            heap[i] = (heap[left[i]] / heap[right[i]])
    else:
        answer = 1
    #
    # # print(f"left:", left)
    # # print(f"right:", right)
    # # print(heap)
    #
    print(heap[1])
    print(f"#{tc} {answer}")