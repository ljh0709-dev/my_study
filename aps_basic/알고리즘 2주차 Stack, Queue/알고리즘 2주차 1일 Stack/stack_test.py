'''
( )( )((( )))
((( )((((( )( )((( )( ))((( ))))))
())
(()
)(
'''
txt = input()
# 스택 생성
top = -1
stack = [0] * 100   # 입력 최대 길이

ans = 1
for x in txt:
    if x == '(':    # 여는 괄호 push
        top += 1
        stack[top] = x
    elif x == ')':  # 닫는 괄호인 경우
        if top == -1:   # 스택이 비어있으면 (여는 괄호가 없으면 )
            ans = 0
            break   # for x
        else:           # 여는 괄호 하나 버림
            top -= 1    # pop
            # 괄호가 여러 종류면 이 부분에서 비교

if top != -1:   # 여는 괄호가 남아있으면
    ans = 0

print(ans)