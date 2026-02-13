import sys
sys.stdin = open('5356의석이의세로로말해요_input.txt')


t = int(input())
for tc in range(1,t+1):
    arr = [list(input().strip()) for _ in range(5)]

    max_row_len = 0     # 단어 중에서 제일 긴 단어의 길이 체크
    for i in arr:
        if max_row_len < len(i):
            max_row_len = len(i)

    for i in arr:       # 최대 길이의 단어와 차이나는 길이만큼 빈문자열 추가
        if len(i) < max_row_len:
            i += [''] * (max_row_len - len(i))

    answer = ''
    for i in range(len(arr[0])):
        for j in range(len(arr)): # 행부터 돌려서 세로로 읽기
            answer += arr[j][i]
    print(f'#{tc} {answer}')
