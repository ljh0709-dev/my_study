def my_len(arr):
    length = 0
    for _ in arr:
        length += 1
    return length

# 선택 정렬
def select_sort(arr):
    n = my_len(arr)

    for i in range(n-1):
        min_idx = i
        for j in range(i+1, n):
            if arr[min_idx] > arr[j]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


a = [5,7,8,2,4,6,1,3]
print(select_sort(a))