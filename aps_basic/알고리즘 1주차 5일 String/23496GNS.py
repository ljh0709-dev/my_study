import sys
sys.stdin = open('23496GNS_input.txt')

t = int(input())

for tc in range(1,t+1):
    n = int(input())
    s = list(map(str, input().split()))
    nums = ["ZRO", "ONE", "TWO", "THR", "FOR", "FIV", "SIX", "SVN", "EGT", "NIN"]
    nums_dict = {}

    for i in range(10):
        nums_dict[i] = nums[i]
    ####################
    #print(nums_dict)

    s_idx = []
    for i in range(10):
        for c in s:
            if nums_dict[i] == c:
                s_idx.append(nums[i])
    #print(s_idx)

    answer = ' '.join(s_idx)
    print(f'#{tc}')
    print(answer)