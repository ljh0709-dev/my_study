import sys; sys.stdin = open("4837 부분집합의 합_input.txt")

def powerset(idx, subset):
    global cnt

    if idx == 12:
        # print(subset)
        if len(subset)==N and sum(subset)==K:
            cnt += 1
        return

    powerset(idx + 1, subset + [A[idx]])
    powerset(idx + 1, subset)

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    A = list(range(1,13))
    N, K = map(int, input().split())
    cnt = 0

    powerset(0,[])
    print(f"#{testcase} {cnt}")