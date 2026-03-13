# 비트 연산 응용
# 1. 1<<n 을 하면 2**n 을 구할 수 있음
# 부분집합의 수를 바로 계산할 수 있
arr = [7,1,3,5]
print(f"부분집합의 수: {1<<len(arr)}개")

# 2. 전체 부분집합을 구할 수 있음
# i = 부분집합 번호
for i in range(1<<len(arr)):
    print(f"{i}번째 부분집합:", end=' ')
    # 각 자리수 모두 확인 -> "각 부분집합에 원소 포함 여부"
    for idx in range(len(arr)):
        if i & (1<<idx):
            print(arr[idx], end = ' ')
    print()
