# 중복순열
# [0,1,2] 3개의 카드가 여러개 존재. (2개를 뽑는 모든 경우)

# 기저조건: 2개의 카드를 모두 뽑았을 경우      ┬ 2단계
# -  시작: 0개의 카드를 고른 상태부터 시작     ┘
# 다음 재귀 호출: 카드 3개 중 하나를 선택      1단계

path = []

def a(x):
    if x == 2:           # 2번 재귀호출 되면, 마지막 레벨이니 출력
        print(path)      # 후에 함수가 리턴되며 종료
        return

    for i in range(3):
        path.append(i)   # 1. 재귀호출 전에 이동할 곳 위치를 기록
        a(x + 1)         # 2. 재귀호출 후에 코드 계속 진행되며 path.append 수행
        path.pop()       # 3. 함수가 종료된 후, 마지막 기록이 삭제되어야 함

a(0)

# [심화] 경로를 전역변수를 사용하지 않고 하는 방법
# - 경로를 누적하면서 pop
def recur(cnt, p):
    if cnt == 2:
        print(*p)
        return

    for i in range(3):
        recur(cnt+1, p + [i])
recur(0, [])