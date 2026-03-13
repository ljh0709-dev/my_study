import sys; sys.stdin = open('1230암호문3_input.txt')

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

        elif prom[idx] == 'D':
            x = int(prom[idx+1])
            y = int(prom[idx+2])
            answer = answer[:x] + answer[x+y:]

        elif prom[idx] == 'A':
            y = int(prom[idx+1])
            s = prom[idx+2:idx+2+y]
            answer = answer + s

    print(f"#{tc}", ' '.join(answer[:10]))