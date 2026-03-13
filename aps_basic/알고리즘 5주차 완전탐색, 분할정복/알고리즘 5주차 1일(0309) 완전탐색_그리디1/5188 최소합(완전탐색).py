import sys; sys.stdin = open('5188 최소합(완전탐색)_input.txt')

# branch: 오른쪽, 아래 2가지 경우 = 2

def solve(r, c, total):
    global dist

    if total >= dist:
        return

    if r==N-1 and c == N-1:
        if dist > total:
            li.append(total)
            dist = total
            return

    for dr, dc in [[0,1], [1,0]]:
        nr = r + dr
        nc = c + dc
        if 0<=nr<N and 0<=nc<N:
            solve(nr, nc, total + arr[nr][nc])
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
t = int(input())
for testcase in range(1,t+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    dist = 13**2*10
    li = []

    solve(0,0,arr[0][0])
    print(li)
    print(f"#{testcase} {dist}")



# # 강사님 코드
# def dfs(x, y, cursum):
#     global ans
#     if ans < cursum
#
#     if x == N-1 and y == N-1:
#         if ans > cursum: ans = cursum
#         return
#     else:
#         if x + 1 < N:
#             dfs(x+1, y, cursum + arr[x+1][y])
#         if y + 1 < N:
#             dfs(x, y+1, cursum + arr[x][y+1])
#
#
# t = int(input())
# for testcase in range(1,t+1):
#     N = int(input())
#     arr = [list(map(int, input().split())) for _ in range(N)]
#     ans = 0xfffffff
#     dfs(0, 0, arr[0][0])
#     print(f'#{testcase} {ans}')