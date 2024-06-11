import time,os,sys
import numpy as np
import cv2
sys.path.append(os.getcwd())
from face_sdk.api_usage.face_helper import FaceHelper



def test():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('无法打开该摄像头')
        exit()

    output_path = 'data/output_frames/temp.jpg'
    face_helper = FaceHelper()
    i = 0
    while True:
        time.sleep(1)
        ret, frame = cap.read()
        cv2.imwrite(output_path, frame)
        if not ret:
            print('无法收到视频帧数据（该视频流是否已结束？），程序正在退出')
            break
        # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        recognizeds = face_helper.rec_face(output_path,0.5)
        cv2.imshow('frame', frame)
        print(recognizeds)
        if cv2.waitKey(1) == ord('F'):
            break

    cap.release()
    cv2.destroyAllWindows()

def add_face(img:str):
    portrait_path = 'data/face/faces/'+img

    facehelper = FaceHelper()
    facehelper.add_face(portrait_path)

if __name__=='__main__':
    # add_face('caigang.jpg')
    test()