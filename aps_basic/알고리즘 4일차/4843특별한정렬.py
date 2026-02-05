import sys
sys.stdin = open('4843특별한정렬_input.txt')


def my_len(li):
    length = 0
    for _ in li:
        length += 1
    return length


def my_sorted(li):
    li = li[:]
    n = my_len(li)

    for i in range(n):
        for j in range(0, n - i - 1):
            if li[j] > li[j + 1]:
                li[j], li[j + 1] = li[j + 1], li[j]
    return li


t = int(input())

for tc in range(1, t + 1):
    n = int(input())
    arr = my_sorted(list(map(int, input().split())))

    half_small = arr[:int(n / 2)]
    half_big = arr[int(n / 2):][::-1]

    special_sort = []
    idx = 0
    while my_len(special_sort) != 10:
        special_sort.append(str(half_big[idx]))
        special_sort.append(str(half_small[idx]))
        idx += 1

    result = ' '.join(special_sort)
    print(f'#{tc} {result}')