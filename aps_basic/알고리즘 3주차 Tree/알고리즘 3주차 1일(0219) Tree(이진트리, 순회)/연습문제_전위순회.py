'''
13
1 2 1 3 2 4 3 5 3 6 4 7 5 8 5 9 6 10 6 11 7 12 11 13
'''

def preorder(t):  # 전위순회, 방문한 정점(부모) 먼저 처리
    if t:   # 0이 아니면 (존재하는 정점이면)
        print(t, end = ' ')    # visit(T) T에서 할일 처리
        preorder(c1[t])  # 왼쪽 자식(서브트리)로 이동
        preorder(c2[t])  # 오른쪽 자식(서브트리)로 이동
    # return None 생략되어있음

def inorder(t):  # 중위순회, 방문한 정점(부모) 먼저 처리
    if t:   # 0이 아니면 (존재하는 정점이면)
        inorder(c1[t])  # 왼쪽 자식(서브트리)로 이동
        print(t, end = ' ')    # visit(T) T에서 할일 처리
        inorder(c2[t])  # 오른쪽 자식(서브트리)로 이동

def postorder(t):  # 후위순회, 방문한 정점(부모) 먼저 처리
    if t:   # 0이 아니면 (존재하는 정점이면)
        postorder(c1[t])  # 왼쪽 자식(서브트리)로 이동
        postorder(c2[t])  # 오른쪽 자식(서브트리)로 이동
        print(t, end = ' ')    # visit(T) T에서 할일 처리



V = int(input())    # 정점 수
E = V - 1       # 간선 수 / V = E + 1
arr = list(map(int, input().split()))

# 부모 번호를 인덱스로 자식 번호를 저장하는 배열
c1 = [0] * (V + 1)  # 왼쪽 자식
c2 = [0] * (V + 1)  # 오른쪽 자식
# 자식 번호를 인덱스로 부모 번호를 저장하는 배열
parents = [0] * (V + 1)

# 고정된 인접리스트
tree = [[0] * 3 for _ in range(V+1)]

for i in range(E):
    p, c = arr[2 * i], arr[2 * i + 1]
    if c1[p] == 0:  # 아직 자식1이 없을 경우
        c1[p] = c
    else:
        c2[p] = c
    parents[c] = p  # 자식을 인덱스로 부모 저장

    if tree[p][0] == 0:  # 왼쪽 자식이 없는 경우
        tree[p][0] = c
    else:
        tree[p][1] = c  # 왼쪽 자식이 있으면
    tree[c][2] = p      # 부모 저장

# for i in tree:
#     print(i)


# root 찾기
c = V       # n번 노드의 부모 찾으려면 n 넣으면 됨
while tree[c][2] != 0:
    c = tree[c][2]
root = c

# root = 1                    # root가 1이라 가정
# for i in range(1, V+1):
#     if parents[i] == 0:     # 부모 없으면 root
#         root = i
#         break



root = 1
for i in range(1, V+1):
    if parents[i] == 0:     # 부모 정점이 없으면 루트
        root = i
        break
preorder(root)    # 1번부터 전위 순회
print()
inorder(root)
print()
postorder(root)
