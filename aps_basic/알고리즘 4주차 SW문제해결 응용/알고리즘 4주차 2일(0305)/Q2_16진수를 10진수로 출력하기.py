import sys; sys.stdin=open('Q2_16진수를 10진수로 출력하기_input.txt')

hex_digits = '0123456789ABCDEF'
hex_bin = {}
for i in hex_digits:
    hex_bin[i] = f"{int(i,16):04b}"


t = int(input())
for tc in range(1,t+1):
    hex_word = input()
    word = ''
    for i in hex_word:
        word += hex_bin[i]
    print(word)

    bin_num = []
    idx = 0
    s = ''
    while idx < len(word):
        if len(s)%7 == 0:
            bin_num.append(s)
            s = ''
        s += word[idx]
        if idx == len(word)-1:
            bin_num.append(s)
        idx += 1
    print(bin_num)

    answer = []
    for i in bin_num[1:]:
        answer.append(int(i,2))
    print(f"#{tc}", *answer)
