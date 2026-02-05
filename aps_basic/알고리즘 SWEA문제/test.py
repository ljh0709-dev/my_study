import sys
input = sys.stdin.readline

n = int(input())

# def take_bong(n):
#     for bong5 in range(n//5, -1, -1):
#         remain = n - bong5 * 5
#         if remain % 3 == 0:
#             bong3 = remain // 3
#             return bong3 + bong5
#     return -1

take = 0
for bong_5kg in range(n//5, -1, -1):    # 5kg 짜리 최대 개수부터 1개씩 줄이며 반복
    sugar = (n - bong_5kg*5)    # nkg 중 5kg 봉지의 개수만큼 무게 제외 후 남은 무게
    if sugar % 3 == 0:    # 남은 무게가 3kg 봉지로 커버되면
          bong_3kg = sugar // 3    # 필요한 3kg 봉지 수
          take = bong_5kg + bong_3kg
          print(take)
          break
else:    # 3kg, 5kg 봉지 조합으로 n이 안되면
    print(-1)