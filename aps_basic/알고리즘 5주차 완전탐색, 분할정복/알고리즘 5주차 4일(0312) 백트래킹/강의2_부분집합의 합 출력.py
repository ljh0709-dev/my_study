# {1,2,3,4,5,6,7,8,9,10}의 부분집합 중, 원소의 합이 10인 부분집합 출력
arr = list(range(1,11))

def powerset(lev, subset):
    # 합이 10 넘으면 리턴
    if sum(subset) > 10:
        return
    
    if lev == len(arr):
        if sum(subset)==10:
            print(subset)
        return

    powerset(lev+1, subset + [arr[lev]])
    powerset(lev+1, subset)

powerset(0,[])
'''
[1, 2, 3, 4]
[1, 2, 7]
[1, 3, 6]
[1, 4, 5]
[1, 9]
[2, 3, 5]
[2, 8]
[3, 7]
[4, 6]
[10]
'''