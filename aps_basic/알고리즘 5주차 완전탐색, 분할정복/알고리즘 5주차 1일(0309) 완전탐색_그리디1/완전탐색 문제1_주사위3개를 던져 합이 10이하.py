# 주사위 3개를 던져서 눈의 합이 10 이하인 경우의 수

# 상태공간트리
# 주사위 3개: depth = 3
# branch 수 : 1~6눈금 = 6

# path = []
# cnt = 0
#
# def recua(x):
#     global cnt
#     if x == 3:
#         if sum(path) <= 10: # 눈의 합이 10 이하라면
#             print(f'{path}: {sum(path)}')
#             cnt += 1
#         return
#
#     for num in range(1,7):
#         path.append(num)
#         recua(x+1)
#         path.pop()
#
# recua(0)
# print(cnt)
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# 위의 코드를 효율적으로 작성
# 1. 이미 10을 넘은 경우 더 체크X
# 2. 누적값을 파라미터로
path2 = []
result = 0
def recua2(x, total):
    global result
    # 이미 눈의 합이 10을 넘은 경우, 더 이상 체크X
    # - 백트래킹의 원리
    if total > 10:
        return

    if x == 3:
        if total <= 10: # 눈의 합이 10 이하라면
            print(f'{path2}: {total}')
            result += 1
        return

    for num in range(1,7):
        path2.append(num)
        recua2(x+1, total + num)
        path2.pop()

recua2(0, 0)
print(result)