import sys
sys.stdin = open('4873반복문자지우기_input.txt')

t = int(input())
for tc in range(1,t+1):
    s = input()

    answer = []
    for i in s:
        answer.append(i)

        if len(answer) >= 2 and answer[-2] == answer[-1]:
            answer.pop()
            answer.pop()

    if answer:
        print(f"#{tc} {len(answer)}")
    else:
        print(f"#{tc} 0")