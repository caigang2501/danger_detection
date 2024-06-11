"""
@author: JiXuan Xu, Jun Wang
@date: 20201024
@contact: jun21wangustc@gmail.com 
"""
import sys,os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import logging
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
import logging.config
logging.config.fileConfig("face_sdk/config/logging.conf")
logger = logging.getLogger('api')

import yaml
import cv2
import numpy as np
from face_sdk.core.model_loader.face_detection.FaceDetModelLoader import FaceDetModelLoader
from face_sdk.core.model_handler.face_detection.FaceDetModelHandler import FaceDetModelHandler
from face_sdk.core.model_loader.face_alignment.FaceAlignModelLoader import FaceAlignModelLoader
from face_sdk.core.model_handler.face_alignment.FaceAlignModelHandler import FaceAlignModelHandler
from face_sdk.core.image_cropper.arcface_cropper.FaceRecImageCropper import FaceRecImageCropper
from face_sdk.core.model_loader.face_recognition.FaceRecModelLoader import FaceRecModelLoader
from face_sdk.core.model_handler.face_recognition.FaceRecModelHandler import FaceRecModelHandler

from tools.ocr_tool import get_video_date

class FaceHelper():
    def __init__(self):
        # common setting for all models, need not modify.
        with open('face_sdk/config/model_conf.yaml') as f:
            model_conf = yaml.load(f,yaml.Loader)
        model_path = 'models'
        self.feature_path = 'data/face/features/name.npy'
        # face detection model setting.
        scene = 'non-mask'
        model_category = 'face_detection'
        model_name =  model_conf[scene][model_category]
        logger.info('Start to load the face detection model...')
        try:
            faceDetModelLoader = FaceDetModelLoader(model_path, model_category, model_name)
            model, cfg = faceDetModelLoader.load_model()
            self.faceDetModelHandler = FaceDetModelHandler(model, 'cpu:0', cfg)
        except Exception as e:
            logger.error('Falied to load face detection Model.')
            logger.error(e)
            sys.exit(-1)
        else:
            logger.info('Success!')

        # face landmark model setting.
        model_category = 'face_alignment'
        model_name =  model_conf[scene][model_category]
        logger.info('Start to load the face landmark model...')
        try:
            faceAlignModelLoader = FaceAlignModelLoader(model_path, model_category, model_name)
            model, cfg = faceAlignModelLoader.load_model()
            self.faceAlignModelHandler = FaceAlignModelHandler(model, 'cpu:0', cfg)
        except Exception as e:
            logger.error('Failed to load face landmark model.')
            logger.error(e)
            sys.exit(-1)
        else:
            logger.info('Success!')

        # face recognition model setting.
        model_category = 'face_recognition'
        model_name =  model_conf[scene][model_category]    
        logger.info('Start to load the face recognition model...')
        try:
            faceRecModelLoader = FaceRecModelLoader(model_path, model_category, model_name)
            model, cfg = faceRecModelLoader.load_model()
            model = model.module.cpu() 
            self.faceRecModelHandler = FaceRecModelHandler(model, 'cpu:0', cfg)
        except Exception as e:
            logger.error('Failed to load face recognition model.')
            logger.error(e)
            sys.exit(-1)
        else:
            logger.info('Success!')
            
    def get_features(self,image_path):
        # read image and get face features.
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        face_cropper = FaceRecImageCropper()
        try:
            dets = self.faceDetModelHandler.inference_on_image(image)
            face_nums = dets.shape[0]
            feature_list = []
            for i in range(face_nums):
                landmarks = self.faceAlignModelHandler.inference_on_image(image, dets[i])
                landmarks_list = []
                for (x, y) in landmarks.astype(np.int32):
                    landmarks_list.extend((x, y))
                cropped_image = face_cropper.crop_image_by_mat(image, landmarks_list)
                feature = self.faceRecModelHandler.inference_on_image(cropped_image)
                feature_list.append(feature)
        except Exception as e:
            logger.error('Pipeline failed!')
            logger.error(e)
            sys.exit(-1)
        else:
            logger.info('Success!')
            return feature_list
        
    def add_face(self,image_path):
        name = image_path.split('/')[-1].split('.')[0]
        features = self.get_features(image_path)
        np.save(self.feature_path.replace('name',name), features[0])
        
    def rec_face(self,img_path,accurecy):
        features = self.get_features(img_path)
        recognizeds = []
        for feature in features:
            recognized = ('',-1)
            for file_name in os.listdir(self.feature_path.split('/name')[0]):
                name = file_name.split('/')[-1].split('.')[0]
                saved_feature = np.load(self.feature_path.split('name')[0]+file_name)
                score = np.dot(saved_feature,feature)
                if score>recognized[1]:
                    recognized = [name,round(float(score),4)]
            recognized = recognized if recognized[1]>accurecy else ['unknown person',round(float(score),4)]
            recognizeds.append(recognized[0])
        return recognizeds
    

if __name__=='__main__':
    pass



