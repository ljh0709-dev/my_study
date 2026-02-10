import sys
sys.stdin = open('22806도로건설_input.txt')

t = int(input())
for tc in range(1, t+1):
    n = int(input())
    arr = [list(map(int,input().split())) for _ in range(n)]


    di = [0, 1, 0, -1]
    dj = [1, 0, -1, 0]

    height = 0
    fee = 1000000

    for i in range(n):
        for j in range(n):
            plus_line = [arr[i][j]]
            #print(f"i,j = {i}, {j}")

            for d in range(4):
                for c in range(1, n):
                    ni = i + di[d]*c
                    nj = j + dj[d]*c
                    if 0<=ni<n and 0<=nj<n:
                        plus_line.append(arr[ni][nj])
            #print(plus_line)


            # 각 + 라인에 위치한 높이의 개수 체크
            cnt = {1:0, 2:0, 3:0, 4:0, 5:0}
            for k in plus_line:
                cnt[k] += 1



            min_cash = 1000000
            choice_h = 0
            # 각 포인트 별 건설 비용 계산
            for h in cnt:
                cash = 0
                for k,v in cnt.items():     # k: 각 도로의 높이(1~5), v: 각 높이 개수
                    cash += v * abs(k-h)

                if min_cash > cash:
                    min_cash = cash
                    choice_h = h
                elif min_cash == cash and choice_h > h:
                    choice_h = h
            #print(f"h: {choice_h}, cash: {min_cash}")

            # 비용 먼저 비교
            if fee > min_cash:
                fee = min_cash
                height = choice_h
            # 비용 같을 때, h가 작으면 해당 값 적용
            elif fee == min_cash:
                if height > choice_h:
                    height = choice_h


    print(f"#{tc} {fee} {height}")