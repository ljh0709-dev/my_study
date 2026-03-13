# def main():
#     x = 3
#     kfc(x+5)
#     print(x)
# def kfc(x):
#     x += 1
#     bts(x+5)
#     print(x)
# def bts(x):
#     print(x)
#
# main()
# def a(x):
#     x+=10
#     print(x, end = ' ')
# def b(x):
#     print(x, end =' ')
#     x += 3
#     a(x+2)
#     print(x, end = ' ')
# x = 3
# b(x+1)
# print(x, end=' ')
# def main():
#     kfc(0)
#     print('end')
# def kfc(x):
#     if x>5:
#         return
#     print(x, end = ' ')
#     kfc(x+1)
#     print(x, end = ' ')
# main()
def a(x):
    print(x)
    if x == 3:
        return

    for i in range(1, 4):
        a(x + 1)

a(0)
