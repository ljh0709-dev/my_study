import sys; sys.stdin = open('1244 최대상금_input.txt')

def change_position(li, change):
    global max_num

    # 숫자판의 길이나 바꾸는 횟수 중 작은거 기준
    if change == n:
        max_num = max(max_num, int(''.join(num)))
        return

    for i in range(length):
        for j in range(i+1, length):
            li[i], li[j] = li[j], li[i]
            change_position(change + 1)
            li[i], li[j] = li[j], li[i]


#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
T = int(input())
for testcase in range(1,T+1):
    # num: 숫자판, n: 바꿀 횟수
    num, n = map(int,input().split())
    num = list(str(num))
    length = len(num)
    max_num = 0

    change_position(0, 0)

    print(f"#{testcase} {max_num}")
