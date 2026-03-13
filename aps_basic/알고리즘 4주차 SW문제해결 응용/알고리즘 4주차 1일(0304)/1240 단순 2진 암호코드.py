import sys; sys.stdin = open("1240 단순 2진 암호코드_input.txt")

secret = {'0001101':0, '0011001':1, '0010011':2, '0111101':3, '0100011':4,
          '0110001':5, '0101111':6, '0111011':7, '0110111':8, '0001011':9}

t = int(input())
for tc in range(1,t+1):
    N, M = map(int, input().split())
    # N: 세로, M: 가로

    code = ''
    for _ in range(N):
        c = input()
        if code:
            continue

        if int(c) != 0:
            code = c


    point = 0   # 암호코드의 마지막 자리 인덱스 찾기
    for i in range(M-1, 0, -1):
        if code[i]=='1':
            point = i
            break
    # 코드 56자로 새로고침
    code = code[point-55:point+1]

    answer = ''
    for i in range(8):
        n = secret[code[7*i : 7*i+7]]
        answer += str(n)
    # print(answer)

    a = 0   # 홀수자리 체크
    b = 0   # 짝수자리 체크
    for i in range(8):
        if i%2==0:
            a += int(answer[i])
        else:
            b += int(answer[i])
    # print(a,b)

    result = 0
    if (a*3 + b)%10 == 0:
        for i in answer:
            result += int(i)

    print(f"#{tc} {result}")