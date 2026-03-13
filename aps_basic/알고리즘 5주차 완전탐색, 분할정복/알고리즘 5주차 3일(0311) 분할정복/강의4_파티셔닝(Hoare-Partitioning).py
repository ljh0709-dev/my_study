# 퀵 정렬
def quick_sort(l,r):
    if l < r:
        s = hoare_partition(l, r):
        quick_sort(l, s-1)
        quick_sort(s+1, r)


# Hoare-Partitioning
# 1. pivot을 정한다
# 2. pivot의 위치를 찾는다.
# - 작은건 왼쪽, 큰건 오른쪽 배치
def hoare_partition(l, r):
    pivot = a[l]    # 피봇 값
    i = l + 1
    j = r
    while i <= j:   # 교차되면 끝
        # i는 pivot보다 큰 값을 검색 (작거나 같으면 i+=1)
        while i <= j and a[i] <= pivot:
            i += 1

        # j는 pivot보다 큰 값을 검색 (크거나 같으면 j-=1)
        while i <= j and a[i] >= pivot:
            r -= 1

        if i < j:
            a[i], a[j] = a[j], a[i]

    # pivot과 j위치를 swap
    arr[l], arr[j] = arr[j], arr[l]
    return j


arr = []
quick_sort(0, len(arr)-1)