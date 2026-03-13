# 이진검색
# [!!주의!!] 이진검색은 항상 정렬된 데이터만 적용

def binary_search(target):
    left = 0                # 검색 시작점
    right = len(arr)-1      # 검색 끝점
    cnt = 0

    while left <= right:    # 교차되는 순간은 target을 못찾음
        mid = (left + right)//2
        cnt += 1

        # 정답을 찾으면 종료
        if arr[mid] == target:
            return mid, cnt

        # arr[mid]가 target보다 큰 경우 = (target이 왼쪽에 위치)
        # mid 기준 왼쪽 탐색
        if arr[mid] > target:
            right = mid - 1

        # arr[mid]가 target보다 작은 경우 = (target이 오른쪽에 위치)
        # mid 기준 오른쪽 탐색
        else:
            left = mid + 1

    return -1, cnt


arr = [7, 4, 2, 9, 11, 23, 19]
arr.sort()
target = [9, 2, 20]
for t in target:
    result = binary_search(t)
    if result[0] != -1:
        print(f"{t}의 위치: {result[0]}, 시도 횟수: {result[1]}")
    else:
        print(f"{t}는 없음, 시도 횟수: {result[1]}")