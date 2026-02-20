# 최대힙

def enq(n):
    global last     # 완전이진트리의 마지막 정점 번호
    last += 1       # 마지막 정점 추가
    heap[last] = n  # 마지막 정점에 key 추가    완전이진트리 유지

    c = last
    p = c // 2      # 완전이진트리에서 부모 정점 번호
    while p and heap[p] < heap[c]: # 부모가 있고, 부모 < 자식 인경우 자리 교환
        heap[p], heap[c] = heap[c], heap[p]
        c = p
        p = c//2

def deq():
    global last             # 완전이진트리의 마지막 정점 번호
    tmp = heap[1]           # 삭제할 루트 원소 백업
    heap[1] = heap[last]    # 삭제할 마지막 노드의 키를 루트에 복사
    last -= 1               # 마지막 노드 삭제    ㅡㅡ여기까지 완전이진트리 유지ㅡㅡ
    p = 1                   # 루트(부모)에 옮긴 값을 자식과 비교
    c = p * 2               # 왼쪽 자식 (비교할 자식 번호)
    while c <= last:        # 자식이 하나라도 있으면 (왼쪽 자식이 있으면)
        if c+1 <= last and heap[c] < heap[c+1]: # 오른쪽 자식도 있고, 오른쪽 자식이 왼쪽 자식보다 더 크면
            c += 1                      # 비교 대상을 오른쪽 자식으로 정함
        if heap[p] < heap[c]:   # 자식이 더 크면 최대힙 규칙에 어긋나므로
            heap[p], heap[c] = heap[c], heap[p]     # 자식과 자리 바꿈
            # 바꾼 자리에서도 자식과 비교해야함
            p = c               # 자식을 새로운 부모로
            c = p // 2          # 왼쪽 자식 번호를 계산
        else:                   # 부모가 더 크면
            break               # 비교 중단,
    return tmp

heap = [0] * 100          # 최대 99개의 데이터가 인큐된다 가정 (99번 노드까지)
last = 0                  # 완전 이진 트리는 1번 정점부터 있음 = 아직 노드 없는 상태

enq(2)
enq(5)
enq(7)
enq(3)
enq(4)
enq(6)
while last:
    print(deq())
