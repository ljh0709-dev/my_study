import sys
sys.stdin = open('부분수열_input.txt')


def my_len(arr):
    length = 0
    for _ in arr:
        length += 1
    return length
##################################################
def my_sum(arr):
    total = 0
    for num in arr:
        total += num
    return total
##################################################
def my_max_idx(arr):
    max_idx = 0
    for i in range(my_len(arr)):
        if arr[max_idx] < arr[i]:
            max_idx = i
    return max_idx
##################################################
def my_min_idx(arr):
    min_idx = 0
    for i in range(my_len(arr)):
        if arr[min_idx] > arr[i]:
            min_idx = i
    return min_idx
##################################################
def subset(arr):
    n = my_len(arr)
    sub_list = []
    for i in range(1, 1<<n): # 공집합 제외한 부분수열 2**n-1개
        sub = []
        for j in range(n):
            if i & (1<<j):
                sub.append(arr[j])
        sub_list.append(sub)
    return sub_list
##################################################
t = int(input())
for tc in range(1,t+1):
    N, M = map(int, input().split())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))

    result = 'YES'
    for sub in subset(B):
        if sub not in subset(A):
            result = 'NO'
            break
    else:
        result = 'YES'

    print(f'#{tc} {result}')
