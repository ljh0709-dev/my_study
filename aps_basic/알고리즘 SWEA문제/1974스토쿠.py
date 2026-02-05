import sys
sys.stdin = open('1974스도쿠.txt')

t = int(input())
for tc in range(1, t+1):
    arr = [list(map(int, input().split())) for _ in range(9)]
    make = 1
    nums = set(range(1, 10))

    # 행 체크
    for row in range(9):
        if set(arr[row]) != nums:
            make = 0
            break

    # 열 체크
    if make == 1:
        for i in range(9):
            col = set(arr[j][i] for j in range(9))
            if col != nums:
                make = 0
                break

    # 박스 체크
    if make == 1:
        for j in range(0, 9, 3):
            for k in range(0, 9, 3):
                box = set()
                for x in range(3):
                    for y in range(3):
                        box.add(arr[j+x][k+y])
                if box != nums:
                    make = 0
                    break

    print(f'#{tc} {make}')
