import sys
sys.stdin = open('반복문1_숫자사각형2_input.txt')

t = int(input())
for tc in range(1,t+1):
    h, w = map(int, input().split())
    # h: 높이, w: 너비

    arr = [[0]*w for _ in range(h)]
    nums = [i for i in range(1,h*w+1)]

    for i in range(h):
        arr[i] = nums[i::h]

    print(f'#{tc}')
    for i in arr:
        print(*i)