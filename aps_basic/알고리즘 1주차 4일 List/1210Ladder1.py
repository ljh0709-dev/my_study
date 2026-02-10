import sys
sys.stdin = open('1210Ladder1_input.txt')


for _ in range(10):
    tc = int(input())
    arr = [list(map(int, input().split())) for _ in range(100)]
    # 행 전체 뒤집어서 내려오기
    ########################################
    i = 99 # 행
    j = 0 # 열
    for idx in range(100):  # 시작 열 찾기
        if arr[99][idx] == 2:
            j = idx
            break
    ########################################
    while i < 100:
        # 1. 왼쪽에 길이 있다면, 끝까지 왼쪽으로
        if j > 0 and arr[i][j-1] == 1:
            while j > 0 and arr[i][j-1] == 1:
                j -= 1

        # 2. 오른쪽에 길이 있다면, 끝까지 오른쪽으로
        elif j < 99 and arr[i][j+1] == 1:
            while j < 99 and arr[i][j+1] == 1:
                j += 1

        # 3. 좌우에 길 없으면 아래로 한 칸
        i += 1
    ########################################
    print(f'#{tc} {j}')


'''
########################################
강사님 풀이
def find_start(arr):
    for i in range(N):
        if arr[N-1][i]==2:
            x = N-1
            y = i
            return x,y
            

def ladder(arr, x, y):  # x 행, y 열
    dx = [0, 0, -1]
    dy = [1, -1, 0]

    while True:
        # 첫 줄에 이동했을 때, y좌표 리턴
        if x == 0: return y
        
        for i in range(3):
            nx = x + dx[i]
            ny = y + dy[i]
            if 0 <= nx < N and 0 <= nx < N:
                x = nx
                y = ny
                arr[x][y] = 'visit' # 방문 체크
                
                
for tc in range(1,11):
    _ = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    # print(arr)
    
    # 맨 아래 행에서 값이 2인 좌표 구하기
    x, y = find_start(arr)
    # 사다리 위로 이동
    print(f"{tc} {ladder(arr,x,y)}")
########################################
'''