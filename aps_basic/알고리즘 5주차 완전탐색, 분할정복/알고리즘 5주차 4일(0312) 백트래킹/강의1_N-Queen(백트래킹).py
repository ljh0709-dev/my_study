# N-Queen
# depth: N
# branch: N
#  일차원 배열로 효율적으로 하는 방법

def check(row):
    for prev_row in range(row):
        # 세로 체크
        if visited[row] == visited[prev_row]:
            return False

        # 열과 행의 차이가 같다 == 현재 col 의 좌우 대각선이다
        # visited 에 저장된 값 = 어느 col에 두었는가 ?
        # row - prev_row = 행의 차이
        # visited[row] - visited[prev_row] = 열의 차이
        # 이 두 개가 같으면 대각선
        if row - prev_row == abs(visited[row] - visited[prev_row]):
            return False

    return True
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
def recur(row):
    global cnt

    if row == N:
        cnt += 1
        return

    for col in range(N):
        visited[row] = col  # 현재 row 의 col 에 놓았다 라고 가정하고
        if not check(row):  # 세로와 대각선을 체크해준다.
            continue

        recur(row + 1)
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    N = int(input())
    visited = [0] * N
    cnt = 0
    recur(0)
    print(f'#{testcase} {cnt}')