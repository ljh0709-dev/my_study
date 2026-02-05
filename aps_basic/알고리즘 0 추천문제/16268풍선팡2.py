import sys
sys.stdin = open('16268풍선팡2_input.txt')

def my_max(n):
    max_value = n[0]
    for i in n:
        if max_value < i:
            max_value = i
    return max_value


t = int(input())

for tc in range(1,t+1):
    n, m = map(int, input().split())
    arr = [list(map(int, input().split())) for _ in range(n)]

    # 우, 하, 좌, 상 순서
    di = [0, 1, 0, -1] # 행
    dj = [1, 0, -1, 0] # 열

    max_value = []

    for i in range(n): # 행
        for j in range(m): # 열
            now = arr[i][j]
            for d in range(4):
                next_i = i + di[d] * arr[i][j]
                next_j = j + dj[d] * arr[i][j]
                # 유효한 인덱스일 때
                if 0 <= next_i < n and 0 <= next_j < m:
                    now += arr[next_i][next_j]

            print(f"i: {i}, j: {j}, {now}")



    #         max_value.append(now)
    # print(f'#{tc} {max_value}')
    #         flower = my_max(now)
    #
    #         if max_value < flower:
    #             max_value = flower
    #
    # print(f'#{tc} {max_value}')
