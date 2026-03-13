import sys; sys.stdin = open("5185이진수_input.txt")

binom_list = [0]*16
for i in range(16):
    n = bin(i)[2:]
    if len(n) < 4:
        n = '0'*(4-len(n)) + n
    binom_list[i] = n

t = int(input())
for tc in range(1,t+1):
    N, num = map(str, input().split())
    answer = ''
    result = ''
    for i in num:
        answer += binom_list[int(i, 16)]
        # result += f"{int(i, 16):04b}"     # f스트링으로 하면 더 간단함. 04b: 4자리 채워서 표현

    print(f"#{tc} {answer}")
    # print(f"#{tc} {result}")