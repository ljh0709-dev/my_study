# ['A', 'J', 'Q', 'K'] 가 각각 넉넉히 있다.
# 카드 5장을 뽑았을 때, 같은 종류의 카드가 3장 연속으로 나오는 경우의 수

cards = ['A', 'J', 'Q', 'K']
path = []
result = 0


# 연속된 3개의 같은 카드가 나오면 return True, 아니면 False
def count_three():
    if path[0] == path[1] == path[2]: return True
    if path[1] == path[2] == path[3]: return True
    if path[2] == path[3] == path[4]: return True
    return False


def recur(cnt):
    global result

    if cnt == 5:
        if count_three():
            result += 1
            print(*path)
        return

    # 카드 중 하나를 선택
    for idx in range(len(cards)):
        path.append(cards[idx])
        recur(cnt + 1)
        path.pop()

recur(0)
print(result)
