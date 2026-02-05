import sys
sys.stdin = open('반복문1_구구단2_input.txt')

t = int(input())
for tc in range(1,t+1):
    s, e = map(int, input().split())
    # s: 시작, e: 끝
    nums = [i for i in range(1,10)]

    print(f'#{tc}')
    if s <= e:
        for i in range(s,e+1):
            gugu = []
            for j in nums:
                if i*j < 10:
                    st = f'{i} * {j} =  {i*j}'
                else:
                    st = f'{i} * {j} = {i*j}'
                gugu.append(st)

            for j in range(0,9,3):
                ans = '   '.join(gugu[j:j+3])
                print(ans)
            print()
    else:
        for i in range(s,e-1,-1):
            gugu = []
            for j in nums:
                if i*j < 10:
                    st = f'{i} * {j} =  {i*j}'
                else:
                    st = f'{i} * {j} = {i * j}'
                gugu.append(st)

            for j in range(0, 9, 3):
                ans = '   '.join(gugu[j:j + 3])
                print(ans)
            print()