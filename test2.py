import shutil
from collections import deque
def filter_out(result_boxs):
    dq_img = deque()
    latest = 0
    result = []
    for num_img,boxs in enumerate(result_boxs):
        if latest!=boxs or len(dq_img)>20:
            if len(dq_img)>0 and latest!=0:
                result.append(f"frame_{dq_img[len(dq_img)//2]}.jpg")
            dq_img.clear()
        latest = boxs
        dq_img.append(num_img)
    
    return result

l = [0,0,0,1,2,1,0]
print(filter_out(l))

