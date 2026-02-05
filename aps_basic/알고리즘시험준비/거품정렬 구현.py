def my_len(arr):
    length = 0
    for _ in arr:
        length += 1
    return length

# 버블 정렬
def bubble_sort(arr):
    n = my_len(arr)

    for i in range(n-1, 0, -1):
        for j in range(i):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


def bubble_sort2(arr):
    n = my_len(arr)
    for i in range(n-1):
        for j in range(i+1, n):
            if arr[j-1] > arr[j]:
                arr[j-1], arr[j] = arr[j], arr[j-1]
    return arr


a = [5,7,8,2,4,6,1,3]
print(bubble_sort(a))
print(bubble_sort2(a))