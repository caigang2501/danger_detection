"""
@author: JiXuan Xu, Jun Wang
@date: 20201015
@contact: jun21wangustc@gmail.com 
"""
import sys
sys.path.append('.')
import logging
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
import logging.config
logging.config.fileConfig("face_sdk/config/logging.conf")
logger = logging.getLogger('api')
import cv2

from face_sdk.core.image_cropper.arcface_cropper.FaceRecImageCropper import FaceRecImageCropper

if __name__ == '__main__':
    image_path = 'face_sdk/api_usage/test_images/tangwei1.jpg'
    image_info_file = 'face_sdk/api_usage/temp/test1_landmark_res0.txt'
    line = open(image_info_file).readline().strip()
    landmarks_str = line.split(' ')
    landmarks = [float(num) for num in landmarks_str]
    
    face_cropper = FaceRecImageCropper()
    image = cv2.imread(image_path)
    cropped_image = face_cropper.crop_image_by_mat(image, landmarks)
    cv2.imwrite('face_sdk/api_usage/temp/test1_cropped.jpg', cropped_image)
    logger.info('Crop image successful!')
