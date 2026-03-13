import sys; sys.stdin = open("5208 전기버스2_input.txt")

def bus(position, charge_cnt):
    global cnt

    if charge_cnt >= cnt:
        return

    # 마지막 정류장 도착
    if position >= N-1:
        # print(path)
        cnt = min(cnt, charge_cnt)
        return

    # 현재 배터리로 갈 수 있는 정류장만 체크
    for i in range(1, battery[position] + 1):
        next_pos = i + position
        path.append(next_pos)
        bus(next_pos, charge_cnt + 1)
        path.pop()

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    arr = list(map(int, input().split()))
    N = arr[0]
    battery = arr[1:]
    cnt = N-1
    path = []

    bus(0, 0)
    print(f"#{testcase} {cnt-1}")

    # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    # 강사님 코드
    ans = 0xFFFFFF
    def dfs(lev, energy, charge):
        global ans

        if lev == N:
            ans = min(ans, charge)
            return

        # 교체하고 통과
        dfs(lev + 1, battery[lev-1]-1, charge + 1)
        # 교체하지 않고 통과(못가는 경우 체크)
        if energy > 0:
            dfs(lev+1, energy-1, charge)

    dfs(1,battery[0],0)
    print(ans)