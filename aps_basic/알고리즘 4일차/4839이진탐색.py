import sys
sys.stdin = open('4839이진탐색_input.txt')

def binary_search(lst, n, k):
    start = 0
    end = n-1
    cnt = 0
    while start <= end:
        middle = (start + end) // 2
        if k == lst[middle]:
            return cnt
        elif k < lst[middle]:   # 찾는 값보다 크면
            end = middle        # 왼쪽 구간 선택
        else:                   # 찾는 값보다 작으면
            start = middle      # 오른쪽 구간 선택
        cnt += 1
    return -1   # 검색 실패


t = int(input())
for tc in range(1,t+1):
    P, A, B = map(int, input().split())
    arr = [i for i in range(1,P+1)]

    A_try = binary_search(arr, P, A)
    B_try = binary_search(arr, P, B)

    if A_try < B_try:
        print(f"#{tc} A")
    elif A_try > B_try:
        print(f"#{tc} B")
    else:
        print(f"#{tc} 0")
