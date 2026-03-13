left = [0, 2, 0, 0, 0]
right = [0, 3, 0, 4, 0]
par = [0, 0, 1, 1, 3]

def postorder(n):
    if n:
        postorder(left[n])
        postorder(right[n])
        print(n, end=' ')
def inorder(n):
    if n:
        inorder(left[n])
        print(n, end=' ')
        inorder(right[n])

postorder(1)
inorder(1)