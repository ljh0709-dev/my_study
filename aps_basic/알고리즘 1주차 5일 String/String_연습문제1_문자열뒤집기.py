import sys
sys.stdin = open('String_연습문제1_문자열뒤집기_input.txt')

t = int(input())

for tc in range(1,t+1):
    n = int(input())
    s = input().strip()

    answer = ''
    for i in range(n-1,-1,-1):
        answer += s[i]
    print(f"#{tc} {answer}")