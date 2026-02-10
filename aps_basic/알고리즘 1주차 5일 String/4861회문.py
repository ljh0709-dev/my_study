import sys
sys.stdin = open('4861회문_input.txt')


def solve(arr, N, M):
    # N : 배열 크기, M : 찾을 문자 길이
    answer = ''
    for i in range(N-M+1):
        for j in range(N):
            if arr[j][i:i+M] == arr[j][i:i+M][::-1]:
                answer = arr[j][i:i+M]

    return answer

########################################
t = int(input())
for tc in range(1,t+1):
    N, M = map(int, input().split())

    # 가로
    arr = [list(input().strip()) for _ in range(N)]
    a = solve(arr,N,M)

    # 세로
    arr2 = list(map(list, zip(*arr)))
    b = solve(arr2,N,M)

    if a:
        print(f'#{tc} {"".join(a)}')
    elif b:
        print(f'#{tc} {"".join(b)}')



