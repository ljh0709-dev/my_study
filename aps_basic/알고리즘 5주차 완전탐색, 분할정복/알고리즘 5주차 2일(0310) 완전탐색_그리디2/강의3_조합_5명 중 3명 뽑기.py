# ['A', 'B', 'C', 'D', 'E'] 5명 중 n명 뽑기
arr = ['A', 'B', 'C', 'D', 'E']
n = 3
path = []

# n명 뽑음: depth = n
# 5명 중 1명 선택: Branch = 5
# 1. 전체 순열 코드부터 시작
# 2. 직전 선택을 다음 재귀호출로 넘겨주고,
#    그 다음부터 선택하도록 구성
def combi(cnt, start):
    if cnt == n:
        print(*path)
        return

    # prev: 이전에 받은 것
    # 중복이 제거된 조합: 이전에 선택했던 것 다음거부터 탐색하자! (i+1)
    # 중복 조합: 이전에 선택했던 것부터 탐색 (i)
    for i in range(start, len(arr)):
        path.append(arr[i])
        combi(cnt + 1, i + 1)   # 이전 선택을 함께 전달
        path.pop()


combi(0, 0) # 중복 허용 호출