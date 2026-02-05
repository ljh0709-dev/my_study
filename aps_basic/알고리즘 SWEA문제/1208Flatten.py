import sys
sys.stdin = open('1208Flatten_input.txt')

def my_min(li):
    min_value = li[0]
    for i in li:
        if min_value > i:
            min_value = i
    return min_value

def my_max(li):
    max_value = li[0]
    for i in li:
        if max_value < i:
            max_value = i
    return max_value


for tc in range(1, 11):
    dump = int(input())
    boxs = list(map(int, input().split()))

    min_idx = boxs.index(my_min(boxs))
    max_idx = boxs.index(my_max(boxs))

    for i in range(dump):
        boxs[min_idx] += 1
        boxs[max_idx] -= 1

        min_idx = boxs.index(my_min(boxs))
        max_idx = boxs.index(my_max(boxs))

    print(f'#{tc} {my_max(boxs) - my_min(boxs)}')