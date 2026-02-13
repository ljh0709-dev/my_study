import sys
sys.stdin = open('11869문자열비교_input.txt')

t = int(input())

for tc in range(1,t+1):
    s1 = input().strip()
    s2 = input().strip()

    if s1 in s2:
        print(f'#{tc} 1')
    else:
        print(f'#{tc} 0')
