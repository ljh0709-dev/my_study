import sys
sys.stdin = open('문제3_파리퇴치_input.txt')

def my_sum(n):
    total = 0
    for i in n:
        total += i
    return total


t = int(input())

for tc in range(1,t+1):
    n, m = map(int, input().split())

    arr = [list(map(int, input().split())) for _ in range(n)]

    max_kill = 0
    for i in range(n-m+1):
        for j in range(n-m+1):
            kill = 0
            for row in arr[i:i+m]:
                kill += my_sum(row[j:j+m])

            if max_kill < kill:
                max_kill = kill

    print(f'#{tc} {max_kill}')