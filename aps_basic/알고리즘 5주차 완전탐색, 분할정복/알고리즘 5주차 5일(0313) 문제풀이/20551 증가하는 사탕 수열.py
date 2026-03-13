import sys
sys.stdin = open('20551 증가하는 사탕 수열_input.txt')
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    # 1번 < 2번 < 3번 되도록
    a, b, c = map(int, input().split())
    candy = 0

    # 처음부터 순증가 되어있으면 굳이 체크X
    if a < b and b < c:
        print(f"#{testcase} {candy}")
        continue

    # 몇 개를 먹어도 순증가가 안되면 컷
    if b < 2 and c < 3:
        candy = -1
        print(f"#{testcase} {candy}")
        continue

    # 2, 3번 상자 먼저 체크
    if b >= c:
        # b를 c보다 1 적게 만들만큼 먹음
        candy += (b - c + 1)
        # 먹고나면 b는 c보다 1 작음
        b = c - 1

    # 1, 2번 상자 체크
    if a >= b:
        candy += (a - b + 1)
        a = b - 1

    if a < 1 or b < 1 or c < 1:
        candy = -1

    print(f"#{testcase} {candy}")