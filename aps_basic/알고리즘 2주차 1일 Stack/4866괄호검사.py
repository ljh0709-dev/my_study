import sys
sys.stdin = open('4866괄호검사_input.txt')

t = int(input())
for tc in range(1,t+1):
    s = input()

    check = []
    for i in s:
        if i in ['(', ')', '{', '}']:
            check.append(i)

        if len(check) >= 2 and (check[-2:] == ['(',')'] or check[-2:] == ['{','}']):
            check.pop()
            check.pop()



    if '(' in check or ')' in check or '{' in check or '}' in check:
        print(f"#{tc} 0")
    else:
        print(f"#{tc} 1")