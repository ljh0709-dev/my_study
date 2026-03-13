import sys; sys.stdin = open("1test.txt")

# 암호 해독기 (0으로 구성되어 있는 앞부분 제외하고 2, 3, 4번째 부분 개수 비율)
decoder = {'211' : 0, '221' : 1, '122' : 2, '411' : 3, '132' : 4,
           '231' : 5, '114' : 6, '312' : 7, '213' : 8, '112' : 9}

# 16개의 숫자에 대한 2진수 표현
hex_dict = {
    '0': '0000', '1': '0001', '2': '0010', '3': '0011',
    '4': '0100', '5': '0101', '6': '0110', '7': '0111',
    '8': '1000', '9': '1001', 'A': '1010', 'B': '1011',
    'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'
}

t = int(input())
for tc in range(1,t+1):
    N, M = map(int, input().split())
    # N: 세로, M: 가로

    # arr = []   # 암호문 있는 행 추출
    arr = list(set([input() for _ in range(N)]))

    # 암호문 찾기
    code_row = []
    for i in range(len(arr)):
        arr[i] = arr[i].strip('0')
        if arr[i] !='':
            code_row.append(arr[i])
    print(f"암호문 있는 행:", code_row)

    # 암호 16진수 변환
    for row in arr:
        hex_row = ''
        for i in row:
            hex_row += hex_dict[i]
        print(hex_row)





    # for _ in range(N):
    #     c = input()
    #     if int(c,16) != 0 and c not in row:
    #         row.append(c)
    # #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    # secret_code = []
    # for c in row:
    #     check = c.strip('0')
    #     secret_code.append(check)
    # #     for i in check:
    # #         if i !='' and i not in secret_code:
    # #             secret_code.append(i)
    # # #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    # test = []
    #
    # for i in range(len(secret_code)):
    #     code = secret_code[i]
    #     length = len(code)
    #     bin_code = ''
    #     for c in code:
    #         bin_code += bin(int(c,16))[2:]
    #         print(bin_code)
    #     print(len(bin_code))
    #         # if len(bin_code)==56:
    #         #     test.append(bin_code)
    #         #     bin_code = ''
    #         #
    #
    #
    # print(f"정렬한 secret_code:", secret_code)
    # #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    #
    # answer = []
    # for c in secret_code:
    #     a = ''
    #     for i in range(8):
    #         n = secret[c[7*i : 7*i+7]]
    #         a += str(n)
    #     answer.append(a)
    # # print(f"answer:", answer)
    # #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    #
    # total = 0
    # for ans in answer:
    #     a = 0   # 홀수자리 체크
    #     b = 0   # 짝수자리 체크
    #     for i in range(8):
    #         if i%2==0:
    #             a += int(ans[i])
    #         else:
    #             b += int(ans[i])
    #
    #     result = 0
    #     # 검증코드까지 정상인 경우
    #     if (a*3 + b)%10 == 0:
    #         for i in ans:
    #             result += int(i)
    #     # print(f"result:", result)
    #     total += result
    #
    # print(f"#{tc} {total}")