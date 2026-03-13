import sys; sys.stdin = open("5186이진수2_input.txt")

n_list = [0]*13
for i in range(1, 14):
    n = 2**(-i)
    n_list[i-1] = n
# print(n_list)


t = int(input())
for tc in range(1,t+1):
    N = float(input())
    M = N

    # a = ''
    # while M != 0:
    #     a += str(int(M*2))
    #     M = M*2 - int(M*2)
    #
    # if len(a) > 12:
    #     a = 'overflow'
    # print(a)

    answer = 0
    b = ['0'] * 13
    cnt = 0
    for i in range(13):
        cnt = i
        answer += n_list[i]
        b[i] = '1'
        if answer == N:
            break
        elif answer > N:
            answer -= n_list[i]
            b[i] = '0'

    result = ''.join(b[:cnt+1])
    if len(result) > 12:
        result = 'overflow'
    print(f"#{tc} {result}")