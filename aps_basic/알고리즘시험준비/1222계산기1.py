import sys; sys.stdin = open('1222계산기1_input.txt')

for tc in range(1,11):
    N = int(input())
    infix = list(input())

    s = []
    postfix = ''
    for i in infix:
        if i.isdigit():
            postfix += i

        else:
            s.append(i)

    while s:
        postfix += s.pop()

    # print(f"#{tc}", postfix)

    s = []
    for i in postfix:
        if i.isdigit():
            s.append(int(i))
        else:
            op2 = s.pop()
            op1 = s.pop()
            s.append(op1 + op2)

    answer = s.pop()
    print(f"#{tc}", answer)