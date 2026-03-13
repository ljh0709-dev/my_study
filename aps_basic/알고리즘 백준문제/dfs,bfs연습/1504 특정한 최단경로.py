import sys; sys.stdin = open('1504 특정한 최단경로_input.txt')

N, E = map(int, input().split())

adj_list = [[] for _ in range(N+1)]

for _ in range(E):
    a, b, c = map(int, input().split())
    adj_list[a].append([b,c])
    adj_list[b].append([a,c])

for i in adj_list:
    print(*i)