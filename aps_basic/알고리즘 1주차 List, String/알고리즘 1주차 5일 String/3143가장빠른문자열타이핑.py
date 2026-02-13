import sys
sys.stdin = open('3143가장빠른문자열타이핑_input.txt')

def my_len(a):
    length = 0
    for _ in a:
        length += 1
    return length


t = int(input())

for tc in range(1,t+1):
    A, B = map(str, input().split())

    A = A.replace(B,'0')
    print(f'#{tc} {my_len(A)}')