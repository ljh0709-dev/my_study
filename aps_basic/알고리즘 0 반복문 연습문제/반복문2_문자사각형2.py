import sys
sys.stdin = open('반복문2_문자사각형2_input.txt')

t = int(input())
for tc in range(1,t+1):
    n = int(input())

    arr1 = [0] * (n*n)
    ascii_list = [chr(i) for i in range(ord('A'), ord('A')+26)]

    for i in range(n*n):
        arr1[i] = ascii_list[i%26]

    arr = []
    for i in range(0, n*n, n):
        if (i//n) % 2 == 0:
            arr.append(arr1[i:i+n])
        else:
            arr.append(arr1[i:i + n][::-1])

    # 전치행렬
    for i in range(n):
        for j in range(i + 1, n):
            arr[i][j], arr[j][i] = arr[j][i], arr[i][j]

    print(f'#{tc}')
    for i in arr:
        print(*i)