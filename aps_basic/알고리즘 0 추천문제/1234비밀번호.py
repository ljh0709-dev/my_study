import sys
sys.stdin = open('1234비밀번호_input.txt')

for tc in range(1,11):
    N, S = map(str, input().split())
    N = int(N)

    check = []
    for i in S:
        check.append(i)

        if len(check) >= 2 and check[-2] == check[-1]:
            check.pop()
            check.pop()

    password = ''.join(check)
    print(f"#{tc} {password}")


