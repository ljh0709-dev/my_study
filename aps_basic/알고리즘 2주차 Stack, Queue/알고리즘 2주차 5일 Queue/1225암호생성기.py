import sys; sys.stdin = open('1225암호생성기_input.txt')


def solve(arr):
    cnt = 1

    q = []
    for i in range(8):
        q.append(arr[i])

    while True:
        # 맨 앞 번호 뽑아냄
        n = q.pop(0)
        n -= cnt
        if n <= 0:
            n = 0
            q.append(n)
            break
        else:
            q.append(n)

        cnt = cnt % 5 + 1

    return q



#t = int(input())
for tc in range(1,11):
    _ = int(input())
    nums = list(map(int, input().split()))

    print(f"#{tc}", *solve(nums))