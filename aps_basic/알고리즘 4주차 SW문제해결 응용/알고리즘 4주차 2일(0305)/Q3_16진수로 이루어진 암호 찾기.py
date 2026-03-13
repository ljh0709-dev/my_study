import sys; sys.stdin=open('Q3_16진수로 이루어진 암호 찾기_input.txt')

def hex_to_bin(n):
    hex_digits = '0123456789ABCDEF'
    hex_bin = {}
    for i in hex_digits:
        hex_bin[i] = f"{int(i,16):04b}"

    return hex_bin[n]

def secret_code(n):
    secret = {'001101':0, '010011':1, '111011':2, '110001':3, '100011':4,
              '110111':5, '001011':6, '111101':7, '011001':8, '101111':9}
    return secret[n]


t = int(input())
for tc in range(1,t+1):
    hex_word = input()
    word = ''
    for i in hex_word:
        word += hex_to_bin(i)
    # print(word, len(word))

    for i in range(len(word)-1, -1,-1):
        if word[i] != '0':
            word = word[:i+1]
            break
    # print(word)

    word_list = []
    idx = len(word) - 1
    w = ''
    while idx > -1:
        if len(w)%6 == 0:
            # 뒤에서부터 체크해서 문자열 w 뒤집어서 추가
            word_list.append(w[::-1])
            w = ''
        w += word[idx]
        if idx == 0:
            # 뒤에서부터 체크해서 문자열 w 뒤집어서 추가
            word_list.append(w[::-1])
        idx -= 1
    # print(word_list)

    word_list = word_list[1:-1][::-1]
    answer = []
    for i in word_list:
        answer.append(secret_code(i))

    print(f"#{tc}", *answer)