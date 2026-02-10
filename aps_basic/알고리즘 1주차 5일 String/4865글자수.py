import sys
sys.stdin = open('4865글자수_input.txt')


t = int(input())

for tc in range(1,t+1):
    s1 = set(input().strip())
    s2 = input().strip()

    char_dict = {}
    for c in s1:
        char_dict[c] = 0


    for c in s2:
        if c in char_dict:
            char_dict[c] += 1


    max_value = 0
    for c in char_dict:
        if max_value < char_dict[c]:
            max_value = char_dict[c]

    print(f'#{tc} {max_value}')