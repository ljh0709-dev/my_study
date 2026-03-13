# 10진수를 2진수로 변환 (n이 양의 정수인 경우)
def decimal_to_binary(n):
    bin_num = ''

    if n == 0:
        return "0"
    # 2로 나눈 나머지를 bin_num에 추가
    # n을 2로 나눈 값이 0보다 크면 2로 계속 나누기
    while n > 0:
        a = n % 2
        bin_num = str(a) + bin_num
        # bin_num += str(a) 하고 리턴할 때 bin_num[::-1] 하면 됨
        n //= 2

    return bin_num
print(f"binary: ", decimal_to_binary(74))
print(bin(74))

# 10진수를 16진수로 변환 (n이 양의 정수인 경우)
def decimal_to_hexadecimal(n):
    hex_digits = '0123456789ABCDEF'
    hex_num = ''

    while n > 0:
        a = n % 16
        hex_num = hex_digits[a] + hex_num
        n //= 16
    return hex_num

print(f"hex: ", decimal_to_hexadecimal(17))
print(hex(17))