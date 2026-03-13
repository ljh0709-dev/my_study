import sys
# input = sys.stdin.readline
sys.stdin = open('practice_input.txt')

adj_list = [[] for _ in range(13)]
for _ in range(12):
    x, y = map(int, input().split())
    adj_list[x].append(y)
    adj_list[y].append(x)

# print(adj_list)

answer = 0
for i in range(1,13):
    star = adj_list[i]
    if len(star) == 3:
        cnt = 0
        for j in star:
            cnt += len(adj_list[j])
        if cnt == 6:
            answer = i
            break
print(answer)
