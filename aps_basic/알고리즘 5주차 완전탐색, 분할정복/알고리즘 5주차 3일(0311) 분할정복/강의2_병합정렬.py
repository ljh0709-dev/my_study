# 병합정렬

# 1. 분할하는 과정
# - depth: 리스트의 길이가 1이 되면 끝
# - branch: 왼쪽과 오른쪽으로 리스트 분할 (2개)
def merge_sort(arr):
    if len(arr) == 1:
        return arr

    mid = len(arr)//2
    left = arr[:mid]    # 왼쪽 절반 리스트
    right = arr[mid:]   # 오른쪽 절반 리스트

    left_list = merge_sort(left)    # 왼쪽
    right_list = merge_sort(right)   # 오른쪽
    # print(f"left_list:", left_list)
    # print(f"right_list:", right_list)

    # 분할한 리스트를 병합
    merge_list = merge(left_list, right_list)

    return merge_list
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# 2. 병합하는 과정 (이때, 정렬하면서 병합)
# - 왼쪽, 오른쪽 리스트 중 가장 작은 원소부터 정답 리스트에 추가
def merge(left, right):
    # 두 리스트를 합한 크기만큼 나옴
    result = [0]*(len(left) + len(right))
    l, r = 0, 0     # 현재 바라보고 있는 인덱스

    # 두 리스트에서 비교할 대상이 남아있을 경우 반복
    while l < len(left) and r < len(right):
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

    return result
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
arr = [69, 10, 30, 2, 16, 8, 31, 22]
print(merge_sort(arr))