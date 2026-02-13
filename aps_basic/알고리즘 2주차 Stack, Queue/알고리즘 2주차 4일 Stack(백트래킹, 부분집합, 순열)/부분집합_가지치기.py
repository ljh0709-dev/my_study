# 부분집합 코드 기본. 이해하고 외워야함

# [1,2,3,4,5,6,7,8,9,10]에서 부분집합의 합이 10인 부분집합 출력

def powerset(level, cur_sum):
    global cnt, all_cnt
    all_cnt += 1

    #ㅡㅡㅡㅡㅡ 가지치기 ㅡㅡㅡㅡㅡ#
    # 현재까지의 합만 고려하기
    if cur_sum > 10:
        return
    #ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
    if level == N:
        if cur_sum == 10:
            cnt += 1

    else:
        # 왼쪽에 1 넣기
        # path[level] = 1
        powerset(level + 1, cur_sum + arr[level])
        # 오른쪽에 0 넣기
        # path[level] = 0
        powerset(level + 1, cur_sum)

arr = [i for i in range(1,11)]
N = len(arr)
path = [0]*N
cnt = 0
all_cnt = 0
powerset(0, 0)
print(f"합이 10인 부분집합 수: {cnt}, 호출횟수: {all_cnt}")