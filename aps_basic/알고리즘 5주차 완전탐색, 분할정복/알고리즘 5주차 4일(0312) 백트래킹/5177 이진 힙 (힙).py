import sys; sys.stdin = open("5177 이진 힙_input.txt")
import heapq

t = int(input())
for tc in range(1,t+1):
    N = int(input())
    nums = list(map(int, input().split()))

    heap = []
    for num in nums:
        heapq.heappush(heap, num)

    heap = [0] + heap
    print(heap)

    # 마지막 원소의 부모 인덱스
    p_idx = N//2
    total = heap[p_idx]
    while p_idx != 0:
        p_idx //= 2
        total += heap[p_idx]


    print(f"#{tc} {total}")