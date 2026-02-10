import sys
sys.stdin = open('22805케익커팅_input.txt')


t = int(input())
for tc in range(1,t+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]

    result = 0  # 불가능 가정

    for i in range(1,N):
        for j in range(1,N):
            strawberry = [0] * 4

            # 상단
            for r in range(i):
                strawberry[0] += sum(arr[r][:j])    # 좌
                strawberry[1] += sum(arr[r][j:])    # 우
            # 하단
            for r in range(i,N):
                strawberry[2] += sum(arr[r][:j])    # 좌
                strawberry[3] += sum(arr[r][j:])    # 우


            if strawberry[0] == strawberry[1] == strawberry[2] == strawberry[3]:
                result = 1      # 4등분 되면 가능
                break

        if result:
            break

    print(f"#{tc} {result}")
