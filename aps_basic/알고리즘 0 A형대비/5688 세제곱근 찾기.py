import sys; sys.stdin = open('5688 세제곱근 찾기_input.txt')

T = int(input())
for testcase in range(1,T+1):
    N = int(input())
    answer = -1

    n = round(N**(1/3))
    if n**3 == N:
        answer = n

    print(f"#{testcase} {answer}")