# 코드 : 5_Stack/powerset_backtrack.py

def backtrack(a, k, n):  # a: 주어진 배열, k: 결정한 원소 수, n: 원소 개수
    c = [0] * MAXCANDIDATES

    if k == n:
        process_solution(a, k)  # 답이면 원하는 작업 수행ㄱ
    else:
        ncandidates = construct_candidates(a, k, n, c)  # 유망한 후보 선택
        for i in range(ncandidates):  # 후보 개수
            a[k] = c[i]
            backtrack(a, k + 1, n)


def construct_candidates(a, k, n, c):  # 후보 추천
    c[0] = True  # 원소의 포함 여부
    c[1] = False
    return 2


def process_solution(a, k):
    for i in range(k):
        if a[i]:
            print(num[i], end=' ')
    print()


MAXCANDIDATES = 2
NMAX = 3
a = [0] * NMAX
num = [1, 2, 3]
backtrack(a, 0, 3)