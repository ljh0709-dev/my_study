import sys
sys.stdin = open('4864문자열비교_input.txt')

def my_max(n):
    max_value = 0
    for i in n:
        if max_value < i:
            max_value = i
    return max_value


t = int(input())
for tc in range(1, t + 1):
    str1 = input().strip()
    str2 = input().strip()

    find_dict = {}
    for i in str1:
        if i not in find_dict:
            find_dict[i] = 0


    for i in str2:
        if i in find_dict:
            find_dict[i] += 1

    count_list = []
    for k, v in find_dict.items():
        count_list.append(v)

    print(f'#{tc} {my_max(count_list)}')