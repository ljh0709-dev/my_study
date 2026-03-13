import sys; sys.stdin = open('5204 병합정렬_input.txt')

# 1. 분할 과정
def merge_sort(arr):
    if len(arr) == 1:
        return arr

    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]

    left_list = merge_sort(left)
    # print(f"left_list: ", left_list)
    right_list = merge_sort(right)
    # print(f"right_list: ", right_list)

    # 분할한 애들 병합해야함
    merge_list = merge(left_list, right_list)
    return merge_list
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# 2. 병합 과정 _ 병합하면서 정렬
def merge(left, right):
    global cnt

    # 왼쪽 마지막 원소가 오른쪽 마지막 원소보다 큰 경우 카운트
    if left[-1] > right[-1]:
        cnt += 1

    result = [0] * (len(left) + len(right))

    l, r = 0, 0     # 각 리스트의 인덱스
    # 두 리스트에서 비교할 대상이 있는 경우에만 반복
    while l < len(left) and r < len(right):
        # 왼쪽 원소가 오른쪽 원소보다 작은 경우 = 정렬된 것
        if left[l] <= right[r]:
            result[l+r] = left[l]
            l += 1
        else:
            result[l+r] = right[r]
            r += 1

    # 남은 데이터들을 모두 result에 추가
    while l < len(left):
        result[l+r] = left[l]
        l += 1

    while r < len(right):
        result[l+r] = right[r]
        r += 1

    # print(f"fin_result:", result)
    return result
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    N = int(input())
    nums = list(map(int, input().split()))
    cnt = 0

    answer = merge_sort(nums)
    print(f"#{testcase} {answer[N//2]} {cnt}")