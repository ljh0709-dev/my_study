import sys; sys.stdin = open('5189 전자카트(순열)_input.txt')

def solve(level, now, total):
    global result
    if total >= result:
        return

    if level == N:
        result = min(result, total + arr[now][0])
        # path.append(arr[now][0])
        # print(path)
        # path.pop()
        return

    for next in range(N):
        if visited[next] == 0:
            visited[next] = 1
            path.append(arr[now][next])
            solve(level + 1, next, total + arr[now][next])
            path.pop()
            visited[next] = 0

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
t = int(input())
for testcase in range(1,t+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    visited = [0]*N
    visited[0] = 1

    path = []
    result = N*N*100

    solve(1, 0, 0)
    print(f"#{testcase} {result}")


#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# 강사님 코드
# Level: N
# Branch: 3
# def perm(lev, cursum):
#     global ans
#     if ans < cursum: return
#
#     if lev == N:
#         # 0-1-2 까지만 포함, 2-0를 추가로 더함
#         cursum += dist[path[N - 1]][path[0]]
#         if ans > cursum: ans = cursum
#         return
#     for i in range(1, N):  # 1부터 반복
#         if used[i]: continue
#         used[i] = 1
#         path.append(i)
#         perm(lev + 1, cursum + dist[path[lev - 1]][path[lev]])
#         path.pop()
#         used[i] = 0
#
#
# T = int(input())
# for tc in range(1, T + 1):
#     N = int(input())
#     dist = [list(map(int, input().split())) for _ in range(N)]
#     path = [0]  # 출발점 0를 추가
#     used = [0] * N
#     used[0] = 1  # 0번은 방문처리
#
#     ans = 987654321
#     perm(1, 0)  # 0를 제외하고 1부터 시작
#     print(f'#{tc} {ans}')
