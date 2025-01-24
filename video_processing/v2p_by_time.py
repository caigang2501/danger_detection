import cv2
import os

def extract_frames(video_path, output_folder,second=1,ordered=False):
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    
    # 获取视频帧速率
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 初始化上一个提取的帧的时间戳
    last_timestamp = -1

    while True:
        # 读取一帧
        ret, frame = cap.read()

        # 检查是否读取到了帧
        if not ret:
            break

        # 计算当前帧的时间戳（秒数）
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / (second*1000.0)

        # 检查与上一个帧的时间戳差异是否大于1秒
        if timestamp - last_timestamp >= 1:
            # 保存帧为图片文件
            if ordered:
                s = f"0000{int(timestamp)}"[-5:]
                output_path = os.path.join(output_folder, f"frame_{s}.jpg")
            else:
                output_path = os.path.join(output_folder, f"frame_{int(timestamp)}.jpg")
            cv2.imwrite(output_path, frame)

            # 更新上一个帧的时间戳
            last_timestamp = timestamp

    # 释放视频捕捉对象
    cap.release()
def mk_vedio_dirtree(root):
    os.mkdir(root)
    os.mkdir(root+'/fired')
    os.mkdir(root+'/frames')
    os.mkdir(root+'/frames/1')
    os.mkdir(root+'/in_area')
    os.mkdir(root+'/no_helmet')

if __name__=='__main__':
    video_path = "data/videos/test copy.mp4"

    root = 'data/asdf'
    frame_folder = root+'/frames/1/'
    ordered_frame_folder = root+'/ordered_frames/1/'
    extract_frames(video_path, frame_folder,second=3)
    extract_frames(video_path, ordered_frame_folder,second=3,ordered=True)
