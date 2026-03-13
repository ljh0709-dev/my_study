import sys; sys.stdin = open('1223계산기2_input.txt')

for tc in range(1,11):
    N = int(input())
    infix = list(input())

    icp = {'*': 2, '+': 1}  # 스택 밖에서의 우선순위
    isp = {'*': 2, '+': 1}  # 스택 안에서의 우선순위

    s = []
    postfix = ''

    for i in infix:
        if i.isdigit():
            postfix += i
        else:
            if s==[] or isp[s[-1]] < icp[i]:
                s.append(i)
            elif isp[s[-1]] >= icp[i]:
                while s and isp[s[-1]] >= icp[i]:
                    postfix += s.pop()
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
            if i == '*':
                s.append(op1 * op2)
            else:
                s.append(op1 + op2)

    answer = s.pop()
    print(F"#{tc} {answer}")