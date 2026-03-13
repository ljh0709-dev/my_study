# 계산기
# 후위 순회를 활용해서 2 + 3 * 4 계산
Tree = [0,'+',2,'*',3,4]
left =  [0,2,0,4,0,0]
right = [0,3,0,5,0,0]
par =   [0,0,1,1,3,3]
c = []

def postorder(t):
    if t:
        postorder(left[t])
        postorder(right[t])
        # print(Tree[t], end=' ')
        if Tree[t] in ['*','+']:
            num2 = c.pop()
            num1 = c.pop()
            if Tree[t]=='*':
                c.append(num1 * num2)
            else:
                c.append(num1 + num2)

        else:
            c.append(Tree[t])

postorder(1)
print(c[0])