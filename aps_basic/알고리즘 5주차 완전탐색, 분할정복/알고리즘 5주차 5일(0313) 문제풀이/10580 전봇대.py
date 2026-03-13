import sys
sys.stdin = open('10580 전봇대_input.txt')
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    N = int(input())
    connect = sorted([list(map(int, input().split())) for _ in range(N)])
    cnt = 0

    # print(connect)
    for a in range(N):
        for b in range(a+1, N):
            # A에 연결된 것 기준으로 정렬했으니
            # 1. 기존 선 A < 새로운 선 A 상태임
            #    기존 선 B > 새로운 선 B 이면 크로스 됨
            if connect[a][1] > connect[b][1]:
                cnt += 1

    print(f"#{testcase} {cnt}")

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡ정렬 안하면 2번 체크해야함ㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# T = int(input())
# for testcase in range(1,T+1):
#     N = int(input())
#     connect = [list(map(int, input().split())) for _ in range(N)]
#     cnt = 0
#
#     for a in range(N):
#         for b in range(a+1, N):
#             # 1. 기존 선 A < 새로운 선 A 상태임
#             #    기존 선 B > 새로운 선 B 이면 크로스 됨
#             if connect[a][0] < connect[b][0] and\
#                     connect[a][1] > connect[b][1]:
#                 cnt += 1
#
#             # 2. 기존 선 A > 새로운 선 A 상태임
#             #    기존 선 B < 새로운 선 B 이면 크로스 됨
#             elif connect[a][0] > connect[b][0] and\
#                     connect[a][1] < connect[b][1]:
#                 cnt += 1
#     print(f"#{testcase} {cnt}")