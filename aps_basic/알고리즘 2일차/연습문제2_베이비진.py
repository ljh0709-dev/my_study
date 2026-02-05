import sys
sys.stdin = open('연습문제2_베이비진_input.txt')

t = int(input())

for tc in range(1, t+1):
    cards = list(input().strip())
    # run : 3장의 카드가 연속적인 번호
    # triplet : 3장의 카드가 동일한 번호
    # baby-gin : 6장의 카드가 run 과 triplet으로 구성

    is_run = is_triplet = 0
    check = [0] * 10
    # 해당 숫자카드 카운트
    for i in cards:
        check[int(i)] += 1

    # triplet 체크 -> 같은 수 3개면 카운트 -3
    for i in range(10):
        while check[i] >= 3:
            check[i] -= 3
            is_triplet += 1

    # run 체크 -> 연속된 3개 수가 카운트 되어있을 때, 각자 카운트 -1씩
    for i in range(8):
        while check[i] and check[i + 1] and check[i + 2]:
            check[i] -= 1
            check[i + 1] -= 1
            check[i + 2] -= 1
            is_run += 1

    # triplet 과 run의 합이 2이면 1, 아니면 0
    if is_triplet + is_run== 2:
        print(f"#{tc} 1")
    else:
        print(f"#{tc} 0")