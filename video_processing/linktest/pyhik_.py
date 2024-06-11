import pyhik.hikvision as hikvision
import cv2

# Initialize the camera object
camera = hikvision.HikCamera('http://10.83.37.30',8000, 'admin', 'zhgd4009')
video_stream = camera.get_video_stream()
print(type(camera),type(video_stream))















