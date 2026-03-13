import sys; sys.stdin = open("5203 베이비진 게임_input(greedy).txt")

def check_triplet_run(li):
    for i in range(10):
        # triplet 체크
        if li[i]==3:
            return True

        # run 체크
        if i <= 7:
            if li[i] and li[i+1] and li[i+2]:
                return True

    return False
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    cards = list(map(int, input().split()))
    player1 = []
    player2 = []
    check_p1 = [0]*10
    check_p2 = [0]*10
    winner = 0
    # 플레이어 카드 배분
    for i in range(0, len(cards), 2):
        player1.append(cards[i])
        check_p1[cards[i]] += 1
        if len(player1) >= 3:   # 3장 이상인 경우부터 체크
            # p1가 triplet이나 run이 있는 경우
            if check_triplet_run(check_p1):
                winner = 1
                break

        player2.append(cards[i+1])
        check_p2[cards[i+1]] += 1
        if len(player2) >= 3:   # 3장 이상인 경우부터 체크
            # p2가 triplet이나 run이 있는 경우
            if check_triplet_run(check_p2):
                winner = 2
                break


    print(f"#{testcase} {winner}")
