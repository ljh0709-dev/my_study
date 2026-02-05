import sys
sys.stdin = open('1206View.txt')


# for tc in range(1,11):
#     n = int(input())
#     arr = list(map(int, input().split()))
#
#     answer = 0
#     for i in range(n):
#         if i == 0:
#             if arr[i] > arr[i+1] and arr[i] > arr[i+2]:
#                 a = arr[i] - arr[i+1]
#                 b = arr[i] - arr[i+2]
#                 if a > b:
#                     answer += b
#                 else:
#                     answer += a
#
#         elif i == n-1:
#             if arr[i] > arr[i-1] and arr[i] > arr[i-2]:
#                 a = arr[i] - arr[i-1]
#                 b = arr[i] - arr[i-2]
#                 if a > b:
#                     answer += b
#                 else:
#                     answer += a
#
#         elif i == 1:
#             if arr[i] > arr[i-1] and arr[i] > arr[i+1] and arr[i] > arr[i+2]:
#                 a = arr[i] - arr[i-1]
#                 if (arr[i] - arr[i+1]) > (arr[i] - arr[i+2]):
#                     b = arr[i] - arr[i+2]
#                 else:
#                     b = arr[i] - arr[i+1]
#                 if a > b:
#                     answer += b
#                 else:
#                     answer += a
#
#         elif i == n-2:
#             if arr[i] > arr[i+1] and arr[i] > arr[i+2] and arr[i] > arr[i-1] and arr[i] > arr[i-2]:
#                 if (arr[i] - arr[i+1]) > (arr[i] - arr[i+2]):
#                     a = arr[i] - arr[i+2]
#                 else:
#                     a = arr[i] - arr[i+1]
#                 if (arr[i] - arr[i-1]) > (arr[i] - arr[i-2]):
#                     b = arr[i] - arr[i-2]
#                 else:
#                     b = arr[i] - arr[i-1]
#                 if a > b:
#                     answer += b
#                 else:
#                     answer += a
#
#         else:
#             if arr[i] > arr[i-1] and arr[i] > arr[i-2] and arr[i] > arr[i+1] and arr[i] > arr[i+2]:
#                 li = [arr[i] - arr[i-1], arr[i] - arr[i-2], arr[i] - arr[i+1], arr[i] - arr[i+2]]
#                 see = li[0]
#                 for i in range(1,4):
#                     if li[i] < see:
#                         see = li[i]
#                 answer += see
#     print(f'#{tc} {answer}')

def n_max(arr):
    max_num = arr[0]
    for i in range(1, len(arr)):
        if max_num < arr[i]:
            max_num = arr[i]
    return max_num

for tc in range(1,11):
    n = int(input())
    arr = list(map(int, input().split()))

    answer = 0
    for i in range(2,n-2):
        if arr[i - 2] < arr[i] and arr[i - 1] < arr[i] and arr[i + 1] < arr[i] and arr[i + 2] < arr[i]:
            near_building = [arr[i - 2], arr[i - 1], arr[i + 1], arr[i + 2]]
            answer += arr[i] - n_max(near_building)
    print(f"#{tc} {answer}")