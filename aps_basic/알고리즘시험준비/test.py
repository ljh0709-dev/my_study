import sys
sys.stdin = open('test_input.txt')

# 첫 줄에 N, 다음에 NxN 문자열. CD 패턴이 존재하는가?
N = int(input())
arr = [list(input().strip()) for _ in range(N)]

ptn = [['A','B'], ['C','D']]
answer = False
for i in range(N-1):
    check = []
    for j in range(N):
        check.append(arr[j][i:i+2])
    print(check)

    for lst in range(N-1):
        if check[lst:lst+2] == ptn:
            print(check[lst:lst+2])
            answer = True
            break
    if answer:
        break
print(f'answer: {answer}')


Z = False
for i in arr:
    if 'Z' in i:
        Z = True
        break
print(f'Z: {Z}')