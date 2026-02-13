import sys; sys.stdin = open('1224계산기3_input.txt')


for tc in range(1,11):
    N = int(input())
    infix = list(map(str, input()))

    icp = {'(': 3, '*': 2, '/': 2, '+': 1, '-': 1}  # 스택 밖에서의 우선순위
    isp = {'(': 0, '*': 2, '/': 2, '+': 1, '-': 1}  # 스택 안에서의 우선순위

    stack = []
    postfix = ''

    for token in infix:
        if token.isdigit():  # 숫자면 후위식에 바로 추가
            postfix += token

        elif token == ')':  # 닫는 괄호면 여는 괄호까지
            while stack and stack[-1] != '(':
                postfix += stack.pop()
            if stack:
                stack.pop()  # '(' 제거
        else:  # 연산자인 경우 '(*/+-'
            if stack == [] or isp[stack[-1]] < icp[token]:
                stack.append(token)
            elif isp[stack[-1]] >= icp[token]:
                while stack and isp[stack[-1]] >= icp[token]:
                    postfix += stack.pop()
                stack.append(token)

    while stack:
        postfix += stack.pop()
    # print(postfix)
    # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ▲후위 표기법 변환▲ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
    # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ▼후위 표기법 연산▼ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#

    stack2 = []
    for tk in postfix:
        if tk.isdigit():  # 숫자면 스택 추가
            stack2.append(int(tk))
        else:
            op2 = stack2.pop()
            op1 = stack2.pop()
            if tk == '*':
                stack2.append(op1 * op2)
            elif tk == '/':
                stack2.append(op1 / op2)
            elif tk == '+':
                stack2.append(op1 + op2)
            elif tk == '-':
                stack2.append(op1 - op2)

    answer = stack2.pop()
    print(f"#{tc} {answer}")