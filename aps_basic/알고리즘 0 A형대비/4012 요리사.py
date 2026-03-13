import sys; sys.stdin = open('4012 요리사_input.txt')


def permul(lev):
    global answer

    if lev == 4:
        # print(li)
        A = li[:2]
        B = li[2:]
        total_A = arr[A[0]][A[1]] + arr[A[1]][A[0]]
        total_B = arr[B[0]][B[1]] + arr[B[1]][B[0]]
        answer = min(answer, abs(total_A - total_B))
        return

    for i in range(N):
        if check[i]:
            continue

        check[i] = 1
        li.append(i)
        permul(lev + 1)
        li.pop()
        check[i] = 0

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    N = int(input())
    a = list(range(N))
    check = [0]*N
    arr = [list(map(int, input().split())) for _ in range(N)]
    answer = 0xFFFFFF
    li = []
    permul(0)

    print(f"#{testcase} {answer}")
