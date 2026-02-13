# 선형 큐 연습문제 (front, rear 활용)
arr = [1, 2, 3]

n = 3
que = [0]*n
front, rear = -1, -1

for i in range(n):
    rear += 1
    que[rear] = arr[i]
print(que)

while front != rear:    # front == rear : 큐가 비어있는 상태
    front += 1
    item = que[front]
    print(item)
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ#
# 선형 큐 연습문제 (append, pop 활용)
q = []
for i in arr:
    q.append(i)

print(q)

for i in range(n):
    print(q.pop(0))