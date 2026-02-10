import sys
sys.stdin = open('연습2_input.txt')

t = int(input())
for tc in range(1,t+1):
    n = int(input())
    box = list(map(int, input().split()))
    # 어떤 원소 box[i]의 오른쪽에 더 작은 수의 개수 찾기

    cnt = []
    for i in range(n-1):
        i_down = 0
        for j in range(i+1, n):
            if box[i] > box[j]:
                i_down += 1
        cnt.append(i_down)
    print(f'#{tc} {max(cnt)}')