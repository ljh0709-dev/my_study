import sys
sys.stdin = open("1931_input.txt")
# input = sys.stdin.readline

N = int(input())

arr = sorted([list(map(int, input().split())) for _ in range(N)],
             key=lambda x: (x[1], x[0]))

end = arr[0][1]
cnt = 1

for i in range(1,N):
    s, e = arr[i]
    if end <= s:
        cnt += 1
        end = e

print(cnt)