import sys
sys.stdin = open('반복문1_합과평균구하기_input.txt')

def my_sum(li):
    s = 0
    for i in li:
        s+=i
    return s


t = int(input())

for tc in range(1,t+1):
    n = int(input())
    arr = list(map(int, input().split()))

    sum_arr = my_sum(arr)
    num = int((sum_arr/n)*100) # 5215
    if num % 10 > 5:
        num += 10
    num //= 10
    avg_arr = num / 10

    print(f"#{tc} {sum_arr} {avg_arr}")

