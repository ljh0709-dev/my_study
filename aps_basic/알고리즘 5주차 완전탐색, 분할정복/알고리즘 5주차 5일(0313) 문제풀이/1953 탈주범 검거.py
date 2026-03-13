import sys
sys.stdin = open('1953 탈주범 검거_input.txt')
from collections import deque
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for _ in range(1,T+1):
    # 지도의 세로 크기 N, 가로 크기 M,
    # 맨홀 뚜껑이 위치한 장소의 세로 위치 R, 가로 위치 C
    # 탈출 후 소요된 시간 L
    N, M, R, C, L = map(int, input().split())
    # 지도
    arr = [list(map(int, input().split())) for _ in range(N)]
    visited = [[0]*M for _ in range(N)]

    # 숫자 1 ~ 7은 해당 위치의 터널 구조물 타입을 의미
    # 숫자 0 은 터널이 없는 장소를 의미
    dr = [0, 1, 0, -1]
    dc = [1, 0, -1, 0]
    dict = {1: [0, 1, 2, 3],
            2: [1,3],
            3: [0,2],
            4: [0,3],
            5: [0,1],
            6: [1,2],
            7: [2,3]}
    # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    def bfs(r,c):
        q = deque()
        q.append([r,c])
        # 1시간 뒤 맨홀로 지하 진입
        visited[r][c] = 1

        while q:
            tr, tc = q.popleft()
            pipe = dict[arr[tr][tc]]
            for d in pipe:
                nr = tr + dr[d]
                nc = tc + dc[d]
                if 0<=nr<N and 0<=nc<M and\
                    visited[nr][nc]==0 and arr[nr][nc]!=0:
                    # 파이프가 연결되어 있는지 체크
                    next = dict[arr[nr][nc]]
                    # 현재 파이프 방향의 반대 방향이 있으면 연결됨
                    if (d+2)%4 in next:
                        q.append([nr,nc])
                        visited[nr][nc] = visited[tr][tc] + 1
    # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    cnt = 0
    bfs(R,C)
    for i in range(N):
        print(visited[i])
        for j in range(M):
            if 0 < visited[i][j] <= L:
                cnt += 1
    print(f"#{_} {cnt}")
