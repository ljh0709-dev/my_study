import sys; sys.stdin = open("5178 노드의 합_input.txt")

def postorder(v):  # 후위순회, 방문한 정점(부모) 먼저 처리
    global N,M

    if v <= N-M:   # 0이 아니면 (존재하는 정점이면)
        postorder(v*2)  # 왼쪽 자식(서브트리)로 이동
        postorder(v*2 + 1)  # 오른쪽 자식(서브트리)로 이동

        if v*2+1 > N:       # 왼쪽 자식만 있는 경우
            heap[v] = heap[v * 2]
        else:               # 양쪽 자식 다 있는 경우
            heap[v] = heap[v * 2] + heap[v * 2 + 1]


t = int(input())
for tc in range(1,t+1):
    # N: 노드 수, M: 리프노드 수, L: 출력할 노드
    N, M, L = map(int, input().split())

    heap = [0] * (N+1)
    for _ in range(M):
        i, num = map(int, input().split())
        heap[i] = num

    postorder(1)
    #print(heap)
    print(f"#{tc} {heap[L]}")
