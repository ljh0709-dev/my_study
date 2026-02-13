import sys; sys.stdin = open('4874Forth_input.txt')

t = int(input())
for tc in range(1, t + 1):
    postfix = list(map(str, input().split()))

    stack = []
    answer = 0

    for token in postfix:
        if token.isdigit():  # 피연산자(숫자)인 경우 push
            stack.append(int(token))
            #print(stack)
        elif token == '.':
            if len(stack) == 1:
                answer = stack.pop()
            else:
                answer = 'error'
        else:  # 연산자면
            if len(stack) >= 2: # stack에 연산 가능한 수가 2개 이상 있으면 연산
                op2 = stack.pop()
                op1 = stack.pop()
                result = 0
                if token == '*':
                    result = op1 * op2
                elif token == '/':
                    result = op1 // op2
                elif token == '+':
                    result = op1 + op2
                elif token == '-':
                    result = op1 - op2
                stack.append(result)
            else:               # 연산 가능한 수가 부족하면 에러
                answer = 'error'
                break


    print(f"#{tc} {answer}")