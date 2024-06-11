import datetime,os
from collections import deque
# lst = [1, 1, 1, 1, 2, 2, 3, 3, 2, 3, 3, 2, 2, 3, 4, 3]
lst =      [0, 0, 1, 1, 0, 1, 1, 2, 2, 3, 3, 2, 3, 3, 2, 0, 2, 3, 4, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
test_imgs= [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
dq_n = 0
dq_img = deque()
v = 1
n = 0
prev,mid = 0,0
prev_img,mid_img = 0,0

result = []
for curr_img,curr in enumerate(lst):
    if prev==curr and prev!=mid:
        mid = curr
        mid_img = curr_img
    else:
        if dq_n!=prev or len(dq_img)>20:
            if len(dq_img)>1 and dq_n!=0:
                result.append(dq_img[len(dq_img)//2])
            dq_img.clear()
        dq_n = prev
        dq_img.append(prev_img)
        prev = mid
        prev_img = mid_img
        mid = curr
        mid_img = curr_img

print(result)
