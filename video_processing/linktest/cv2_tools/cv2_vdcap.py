import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print('无法打开该摄像头')
    exit()

while True:
    # 逐帧捕捉
    ret, frame = cap.read()
    
    # 如果帧读取正确，ret 为 True
    if not ret:
        print('无法收到视频帧数据（该视频流是否已结束？），程序正在退出')
        break
    
    # 转换该视频帧为灰度图像
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    all_color = cv.cvtColor(frame, cv.COLOR_RGB2RGBA)
    # 显示该帧
    cv.imshow('frame', all_color)
    # 当按下键盘 q 时，退出程序
    if cv.waitKey(1) == ord('q'):
        break

# 当程序结束时，释放该摄像头资源
cap.release()
cv.destroyAllWindows()