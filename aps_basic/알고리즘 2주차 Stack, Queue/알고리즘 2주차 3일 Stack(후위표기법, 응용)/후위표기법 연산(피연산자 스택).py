# (6 + 5 * (2 - 8) / 2)
# 6528-*2/+
stack = [0] * 10    # stack = [] 로 하면 append, pop로 체크
top = -1

icp = {'(':3, '*':2, '/':2, '+':1, '-':1}    # 스택 밖에서의 우선순위
isp = {'(':0, '*':2, '/':2, '+':1, '-':1}    # 스택 안에서의 우선순위

infix = '6+5*(2-8)/2' # 중위식 문자열
postfix = ''    # 후위식 문자열

for token in infix:
    if token not in '(*/+-)':   # 피연산자면 후위식에 바로 추가
        postfix += token
    elif token == ')':          # 닫는 괄호면 여는 괄호를 만날 때까지
        while top > -1 and stack[top] != '(':   # 여는괄호 만날때까지 pop
            top -= 1
            postfix += stack[top + 1]       # pop한 것을 후위식에 추가
        # append()로 했을 경우
        # while stack and stack[-1] != '(':
        #   postfix += stack.pop()
        if top != -1:
            top -= 1    # '(' 제거
    else:                       # 연산자인 경우 '(*/+-'
        if top == -1 or isp[stack[top]] < icp[token]:
            top += 1
            stack[top] = token
        elif isp[stack[top]] >= icp[token]:
            while top > -1 and isp[stack[top]] >= icp[token]:
                top -= 1
                postfix += stack[top + 1]
            top += 1                # 스택의 마지막 연산자보다
            stack[top] = token      # 우선순위가 높아졌으니 push
    print(postfix, stack, top)

while top > -1:
    top -= 1
    postfix += stack[top+1]
print(postfix)

#################################################
### 후위표기법 연산 ###
stack2 = []
for token in postfix:
    if token not in '*/+-':     # 피연산자면 push
        stack2.append(int(token))    # token은 문자열이라 int 씌움
    else:                       # 연산자면
        op2 = stack2.pop()
        op1 = stack2.pop()
        if token == '*':
            stack2.append(op1 * op2)
        elif token == '/':
            stack2.append(op1 / op2)
        elif token == '+':
            stack2.append(op1 + op2)
        elif token == '-':
            stack2.append(op1 - op2)

answer = stack2.pop()
print(answer)