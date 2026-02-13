import sys; sys.stdin = open('11673반사경_input.txt')


t = int(input())
for tc in range(1,t+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    # 0: 빈 곳, 1: / 거울, 2: \ 거울  => 총 반사되는 거울 수

    # 우, 하, 좌, 상
    dr = [0, 1, 0, -1]
    dc = [1, 0, -1, 0]

    # (0,0)부터 오른쪽으로 진행
    r = c = direct = 0
    mir = 0

    while True:
        nr = r + dr[direct]
        nc = c + dc[direct]
        if not (0 <= nr < N and 0 <= nc < N):
            # 레이저 범위 밖으로 나가면 끝
            break

        else:
            if arr[nr][nc] == 1:
                # 오 -> 위, 아래 -> 좌, 왼 -> 아래, 위 -> 오
                direct = [3, 2, 1, 0][direct]
                mir += 1
            elif arr[nr][nc] == 2:
                # 오 -> 아래, 아래 -> 오, 왼 -> 위, 위 -> 왼
                direct = [1, 0, 3, 2][direct]
                mir += 1

            r = nr
            c = nc

    print(f"#{tc} {mir}")