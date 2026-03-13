import sys
sys.stdin = open('1486 장훈이의 높은 선반_input.txt')
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for _ in range(1,T+1):
    N, B = map(int, input().split())
    people = sorted(list(map(int, input().split())))
    S = sum(people)
    # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    def powerset(lev, subset, h):
        global height
        if h >= height:
            return

        if lev == N:
            if h >= B:
                height = min(height, h)
                # print(subset, h)
            return

        powerset(lev + 1, subset + [people[lev]], h + people[lev])
        powerset(lev + 1, subset, h)
    # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    height = 0xFFFFFF
    powerset(0, [], 0)
    print(f"#{_} {height - B}")