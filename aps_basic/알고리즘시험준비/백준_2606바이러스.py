import sys; sys.stdin = open('백준_2606바이러스.txt')


def dfs(v):
    global cnt

    visited[v] = True
    cnt += 1
    for w in adj_list[v]:
        if visited[w] == False:
            dfs(w)
    return

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
com = int(input())
pair = int(input())

adj_list = [[] for _ in range(com+1)] # 인접리스트
visited = [False] * (com+1)   # 방문리스트

for i in range(pair):
    start, end = map(int, input().split())
    adj_list[start].append(end)
    adj_list[end].append(start)     # 양방향

cnt = -1
dfs(1)

print(cnt)