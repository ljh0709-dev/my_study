import sys; sys.stdin = open('5097회전_input.txt')

t = int(input())
for tc in range(1, t + 1):
    N, M = map(int, input().split())
    nums = list(map(int, input().split()))

    for _ in range(M):
        a = nums.pop(0)
        nums.append(a)

    print(f"#{tc} {nums[0]}")