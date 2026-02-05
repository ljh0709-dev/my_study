import sys
sys.stdin = open('반복문1_짝수홀수개수구하기_input.txt')

t = int(input())

for tc in range(1,t+1):
    n = int(input())
    arr = list(map(int, input().split()))

    a = b = 0
    for i in arr:
        if i % 2 == 0:
            a+=1
        else:
            b+=1
    print(f'#{tc} {a} {b}')