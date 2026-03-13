path = []

def recur(x):
    if x == 3:
        print(path)
        return

    for i in range(1,7):
        path.append(i)
        recur(x+1)
        path.pop()
recur(0)

# path2 = []
#
# def recur2(x):
#     if x == 5:
#         print(path2)
#         return
#
#     for i in range(1,5):
#         path2.append(i)
#         recur2(x+1)
#         path2.pop()
# recur2(0)