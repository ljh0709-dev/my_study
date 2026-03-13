import sys; sys.stdin=open('Q1_2진수를 10진수로 출력하기_input.txt')

t = int(input())
for tc in range(1,t+1):
    word = input()

    answer = []
    for i in range(0, len(word), 7):
        w = word[i:i+7]
        answer.append(int(w,2))
    print(f"#{tc}", *answer)