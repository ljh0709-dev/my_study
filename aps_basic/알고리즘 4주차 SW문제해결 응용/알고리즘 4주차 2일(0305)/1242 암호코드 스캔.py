import sys; sys.stdin = open("1242 암호코드 스캔_input.txt")

# 암호코드 비율에 따른 맵핑
arr = ['0001101', '0011001', '0010011', '0111101', '0100011',
       '0110001', '0101111', '0111011', '0110111', '0001011']
secret = {}
for i in range(10):
    scan = arr[i]
    decoder = ''
    for j in range(1,6):
        for s in scan:
            decoder += s * j
        secret[decoder] = i
        decoder = ''
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# 16진수를 2진수로 바꾼 맵핑
hex_digits = '0123456789ABCDEF'
hex_bin = {}
for i in hex_digits:
    hex_bin[i] = f"{int(i,16):04b}"
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
t = int(input())
for tc in range(1,t+1):
    N, M = map(int, input().split())
    # N: 세로, M: 가로

    row = []   # 암호문 있는 행 추가
    for _ in range(N):
        c = input().strip()
        if int(c,16) != 0 and c not in row:
            row.append(c)
    # print(f"암호문 있는 행:", row)
    #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    # 암호문 찾기
    change_code = []
    for code_row in row:
        r = code_row.rstrip('0')
        # print(f"r:", r)

        change = ''
        for i in r:
            change += hex_bin[i]
        change = change.rstrip('0')
        change_code.append(change)

    # print(f"이진수 변환 암호문:", change_code)
    # #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    secret_code = []
    for c in change_code:
        bin_code = c
        code = ''
        check = ''
        idx = len(bin_code) - 1
        while idx > -1:
            check = bin_code[idx] + check
            if check in secret:
                code = str(secret[check]) + code
                check = ''
            idx -= 1

            if len(code) == 8:
                secret_code.append(code)
                code = ''
                bin_code = bin_code[:idx].rstrip('0')
                idx = len(bin_code) - 1

    secret_code = list(set(secret_code))

    # print(f"secret_code:", secret_code)
    # #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    answer = 0
    for code in secret_code:
        a = int(code[0]) + int(code[2]) + int(code[4]) + int(code[6])
        b = int(code[1]) + int(code[3]) + int(code[5]) + int(code[7])

        if (a*3 + b) % 10 == 0:
            answer += (a + b)
    # print(f"answer:", answer)
    # #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
    print(f"#{tc} {answer}")