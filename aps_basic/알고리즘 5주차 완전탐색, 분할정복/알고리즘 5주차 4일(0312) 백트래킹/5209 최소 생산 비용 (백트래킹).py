import sys; sys.stdin = open("5209 최소 생산 비용_input.txt")

def solve(row, now_sum):
    global pay

    # 현재 합이 최소생산비용보다 크면 패스
    if now_sum > pay:
        return

    # depth: N
    if row == N:
        print(*path, now_sum)
        pay = now_sum
        return

    # branch: N
    for col in range(N):
        # 방문한 공장이면 패스
        if visited[col]:
            continue

        visited[col] = 1
        path.append(f"{col}: {arr[row][col]}")
        solve(row + 1, now_sum + arr[row][col])
        path.pop()
        visited[col] = 0

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    path = []
    visited = [0]*N
    pay = 0xFFFFFF

    solve(0,0)
    print(f"#{testcase} {pay}")