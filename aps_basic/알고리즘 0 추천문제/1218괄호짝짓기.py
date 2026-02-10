import sys
sys.stdin = open('1218괄호짝짓기_input.txt')

for tc in range(1,11):
    n = int(input())
    s = input()

    check = []

    for i in s:
        if i in ['(', ')', '[', ']', '{', '}', '<', '>']:
            check.append(i)

            if len(check) >= 2 and check[-2:] in [['(', ')'], ['[', ']'], ['{', '}'], ['<', '>']]:
                check.pop()
                check.pop()

    if check:
        print(f"#{tc} 0")
    else:
        print(f"#{tc} 1")