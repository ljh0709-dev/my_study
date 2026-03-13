import sys; sys.stdin = open('5205 퀵정렬_input.txt')

def quick_sort(left, right):
    if left < right:
        pivot = hoare_partition(left, right)
        quick_sort(left, pivot - 1)
        quick_sort(pivot + 1, right)
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
def hoare_partition(left, right):
    pivot = nums[left]   # 제일 왼쪽 요소
    l = left + 1
    r = right

    while l <= r:    # 교차되면 종료
        # l은 pivot보다 큰 값을 선택 (작거나 같으면 l += 1)
        while l <= r and nums[l] <= pivot:
            l += 1

        # r은 pivot보다 작은 값을 선택 (크거나 같으면 r -= 1)
        while l <= r and nums[r] >= pivot:
            r -= 1

        if l < r:   # swap
            nums[l], nums[r] = nums[r], nums[l]

    # pivot과 r의 위치를 swap
    nums[left], nums[r] = nums[r], nums[left]
    return r

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    N = int(input())
    nums = list(map(int, input().split()))

    quick_sort(0, N-1)
    print(f"#{testcase} {nums[N//2]}")