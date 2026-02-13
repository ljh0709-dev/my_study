t = int(input())
for tc in range(1, t + 1):
    N = int(input())
    # A: 전, B: 후
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))

    cnt = 0
    for i in range(N):
        # 상태 같으면 패스
        if A[i] == B[i]:
            continue
        else:  # 다르면 스위치 딸깍
            for j in range(i, N):  # i 이후 전체 반전
                A[j] = 1 - A[j]
            cnt += 1

        if A == B:
            break
    print(f"#{tc} {cnt}")