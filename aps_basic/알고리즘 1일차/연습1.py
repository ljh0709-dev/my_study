import sys
sys.stdin = open('연습1_input.txt')

T = int(input())
for tc in range(1,T+1):
    n = int(input())
    arr = list(map(int, input().split()))

    max_num = min_num = arr[0]

    for i in range(1, n):
        if max_num < arr[i]:
            max_num = arr[i]
        if min_num > arr[i]:
            min_num = arr[i]

    print(f'#{tc} {max_num - min_num}')