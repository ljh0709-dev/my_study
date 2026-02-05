import sys
sys.stdin = open('4방향_input.txt')


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
def my_abs(n):
    if n > 0:
        return n
    else:
        return n*(-1)
##################################################
def solve(arr, n):
    # 우, 하, 좌, 상
    di = [0, 1, 0, -1] # 행
    dj = [1, 0, -1, 0] # 열

    result = 0

    for i in range(n):
        for j in range(n):
            s = 0
            for d in range(4):
                n_i = i + di[d]
                n_j = j + dj[d]
                if 0 <= n_i < n and 0 <= n_j < n:
                    s += my_abs(arr[i][j] - arr[n_i][n_j])
            result += s
    return result
##################################################
T = int(input())
for tc in range(1,T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    print(f'#{tc} {solve(arr, N)}')