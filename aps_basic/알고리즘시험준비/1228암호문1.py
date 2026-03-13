import sys; sys.stdin = open('1228암호문1_input.txt')

for tc in range(1,11):
    N = int(input())
    secret = list(map(str, input().split()))
    p = int(input())
    prom = list(map(str, input().split()))


    answer = secret[:]

    for idx in range(len(prom)):
        if prom[idx] =='I':
            x = int(prom[idx+1])
            y = int(prom[idx+2])
            s = prom[idx+3:idx+3+y]

            answer = answer[:x] + s + answer[x:]

    print(f"#{tc}", ' '.join(answer[:10]))


