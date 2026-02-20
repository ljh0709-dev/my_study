# 최소힙만 지원
import heapq
heap = [7,2,5,3,4,6]
heapq.heapify(heap)     # 한번에 힙으로 변환

print(heap) # 인덱스 0도 씀
heapq.heappush(heap, 1)
print(heap)
while heap:
    print(heapq.heappop(heap), end=' ')
print()
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# 최대힙 -> 음수 붙여서 하면 됨
a = [7,2,5,3,4,6]
heap2 = []
for i in range(len(a)):
    heapq.heappush(heap2, -a[i])
print(heap2)
while heap2:
    print(heapq.heappop(heap2)*-1, end=' ')
print()