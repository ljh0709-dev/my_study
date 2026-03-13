# 완전탐색으로 부분집합 구하기
# 3명의 친구 부분집합 만들기

arr = ['O', 'X']
path = []
# 3명의 친구 : depth = 3
# O, X중 하나 선택 : Branch = 2

def recur(cnt):
    if cnt == 3:
        print(*path)
        return

    for i in range(2):
        path.append(arr[i])
        recur(cnt + 1)
        path.pop()

    # # O를 선택 (부분집합에 포함되는 경우)
    # path.append(arr[0])
    # recur(cnt + 1)
    # path.pop()
    #
    # # X를 선택 (포함 안되는 경우)
    # path.append(arr[1])
    # recur(cnt + 1)
    # path.pop()


recur(0)
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# 아래 코드를 조금 더 많이 활용하게 될 것
name = ['MIN', 'CO', 'TIM']


def solve(idx, subset):
    if idx == 3:
        print(*subset)
        return

    # 포함하는 경우
    solve(idx + 1, subset + [name[idx]])

    # 안하는 경우
    solve(idx + 1, subset)


solve(0, [])