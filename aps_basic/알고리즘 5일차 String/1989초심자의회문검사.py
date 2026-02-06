import sys
sys.stdin = open('1989초심자의회문검사_input.txt')

t = int(input())
for tc in range(1,t+1):
    s = input().strip()
    if s == s[::-1]:
        print(f'#{tc} 1')
    else:
        print(f'#{tc} 0')