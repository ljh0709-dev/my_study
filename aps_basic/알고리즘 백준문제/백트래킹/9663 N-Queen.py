# def queen(row):
#     global cnt
#
#     if row == n:
#         cnt += 1
#         print(path)
#         return
#
#     for col in range(n):
#         path[row] = col     # 각 행에서 퀸을 놓은 열 체크
#
#         for i in range(row):
#             if path[i] == path[row] or abs(path[row] - path[i]) == row - i:
#                 break
#         else:
#             queen(row + 1)
# #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# n = 5
# # n = int(input())
# path = [0] * n
# cnt = 0
#
# queen(0)
# print(cnt)
# #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
def safe(row):
    # 같은 열에 퀸이 있는지 체크
    for i in range(row):
        if col[row] == col[i] or \



N = 4
col = [0] * N




















