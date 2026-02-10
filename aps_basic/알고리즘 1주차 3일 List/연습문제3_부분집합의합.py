import sys
sys.stdin = open('연습문제3_부분집합의합_input.txt')

def my_sum(li):
    s = 0
    for i in li:
        s += i
    return s


t = int(input())
for tc in range(1,t+1):
    n = int(input())
    arr = list(map(int, input().split()))

    subset_sum_zero = False

    for i in range(1, 1<<n):   # n: 원소 개수
        subset = []
        for j in range(n):  # 원소 수 만큼 비트 비교
            if i & (1<<j):  # i의 j번 비트가 1이면
                subset.append(arr[j])
        if my_sum(subset) == 0:
            subset_sum_zero = True
            break

    if subset_sum_zero:
        print(f'#{tc} 1')
    else:
        print(f'#{tc} 0')
