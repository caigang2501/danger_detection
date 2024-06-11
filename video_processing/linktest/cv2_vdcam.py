import cv2

# 摄像头的地址、端口、用户名和密码
camera_address = "http://admin:zhgd4009@10.83.37.30:8000/ISAPI/Streaming/channels/101"

# 创建一个 VideoCapture 对象，参数为摄像头的 URL
cap = cv2.VideoCapture(camera_address)

# 检查摄像头是否被正确打开
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# 不断循环读取摄像头的视频帧
while True:
    # 读取视频帧
    ret, frame = cap.read()

    # 检查视频帧是否成功读取
    if not ret:
        print("Error: Could not read frame.")
        break

    # 在这里您可以对视频帧进行处理，例如显示、保存等
    cv2.imshow('Frame', frame)

    # 按下 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 关闭摄像头并销毁所有窗口
cap.release()
cv2.destroyAllWindows()
