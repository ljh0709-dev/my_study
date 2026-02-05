import sys
sys.stdin = open('반복문1_구구단1_input.txt')

t = int(input())
for tc in range(1,t+1):
    s, e = map(int, input().split())
    # s: 시작, e: 끝
    nums = [i for i in range(1, 10)]

    print(f'#{tc}')
    if s <= e:
        for j in nums:
            gugu = []
            for i in range(s, e+1):
                if j*i < 10:
                    st = f'{i} * {j} =  {i*j}'
                else:
                    st = f'{i} * {j} = {i*j}'
                gugu.append(st)

            print('   '.join(gugu))

    else:
        for j in nums:
            gugu = []
            for i in range(s, e-1, -1):
                if j * i < 10:
                    st = f'{i} * {j} =  {i * j}'
                else:
                    st = f'{i} * {j} = {i * j}'
                gugu.append(st)

            print('   '.join(gugu))