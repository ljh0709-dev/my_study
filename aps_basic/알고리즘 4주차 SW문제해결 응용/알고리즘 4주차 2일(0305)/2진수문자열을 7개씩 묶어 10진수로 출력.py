def f(bin_str):
    # 전달받은 문자열을 뒤에서부터 탐색
    # 10진수로 변환하며 계산
    result = 0
    for i in range(6,-1,-1):
        result += int(bin_str[i]) * 2**(7-1-i)

    return result


words = '0000000111100000011000000111100110000110000111100111100111111001100111'# list(input())
answer = []
for i in range(0, len(words), 7):
    word = words[i:i+7]
    answer.append(f(word))

print(*answer)