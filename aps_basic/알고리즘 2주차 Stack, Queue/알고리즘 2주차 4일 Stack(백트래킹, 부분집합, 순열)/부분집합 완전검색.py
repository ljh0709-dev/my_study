# 부분집합 코드 기본. 이해하고 외워야함

# [1,2,3,4,5,6,7,8,9,10]에서 부분집합의 합이 10인 부분집합 출력

def powerset(level):
    global cnt, all_cnt
    all_cnt += 1
    if level == N:
        # 각 부분집합의 합을 계산
        sum_v = 0
        for i in range(N):
            if path[i] == 1:
                sum_v += arr[i]
        # 합이 10인 경우 출력
        if sum_v == 10:
            cnt += 1
            for i in range(N):
                if path[i]==1:
                    print(arr[i], end = ' ')
            print()


    else:
        # 왼쪽에 1 넣기
        path[level] = 1
        powerset(level+1)
        # 오른쪽에 0 넣기
        path[level] = 0
        powerset(level+1)

arr = [i for i in range(1,11)]
N = len(arr)
path = [0]*N
cnt = 0
all_cnt = 0
powerset(0)
print(f"cnt: {cnt}, all_cnt: {all_cnt}")