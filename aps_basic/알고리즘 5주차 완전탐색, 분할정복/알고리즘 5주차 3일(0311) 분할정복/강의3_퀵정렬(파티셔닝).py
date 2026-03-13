# 퀵 정렬

def quickSort(a, l, r):
    if l < r:
        s = partition(a, l, r)
        quickSort(a, l, s+1)
        quickSort(a, s+1, r)


# Partitioning
# Pivot의 위치를 고정
def partition(arr, l, r):
    pass



