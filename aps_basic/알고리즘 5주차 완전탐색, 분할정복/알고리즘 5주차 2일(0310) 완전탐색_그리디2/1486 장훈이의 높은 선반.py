import sys; sys.stdin = open('1486 장훈이의 높은 선반_input.txt')

def powerset(level, subset):
    # Branch: 2 (해당 직원 포함하냐 안하냐)
    # Level: N
    global answer

    if level == N:
        height = sum(subset)
        if height >= B:
            answer = min(answer, height)
        return

    powerset(level+1, subset + [people[level]])
    powerset(level+1, subset)


#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    # N: 점원 수, B: 선반 높이
    N, B = map(int, input().split())
    people = sorted(list(map(int, input().split())), reverse=True)
    answer = sum(people)    # S: 직원 키 총 합

    powerset(0, [])
    print(f"#{testcase} {answer-B}")