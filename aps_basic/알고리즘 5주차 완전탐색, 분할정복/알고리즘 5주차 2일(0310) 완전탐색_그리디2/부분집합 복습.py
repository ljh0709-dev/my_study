def powerset(level, now_sum):
    if level == N:
        print(now_sum)
        return

    # Branch: 2
    # Level: N
    # for i in range(2):
    #     path.append(i)
    #     powerset(level+1)
    #     path.pop()

    # 포함하는 경우
    # path.append(arr[level])
    powerset(level + 1, now_sum + arr[level])
    # path.pop()
    # 포함하지 않는 경우
    powerset(level + 1, now_sum)



arr = list(range(1,11))
# path = []
N = len(arr)
powerset(0, 0)