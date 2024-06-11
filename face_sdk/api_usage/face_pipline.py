"""
@author: JiXuan Xu, Jun Wang
@date: 20201024
@contact: jun21wangustc@gmail.com 
"""
import sys,os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
sys.path.append('.')
import logging
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
import logging.config
logging.config.fileConfig("face_sdk/config/logging.conf")
logger = logging.getLogger('api')

import yaml
import cv2
import torch
import numpy as np
from face_sdk.core.model_loader.face_detection.FaceDetModelLoader import FaceDetModelLoader
from face_sdk.core.model_handler.face_detection.FaceDetModelHandler import FaceDetModelHandler
from face_sdk.core.model_loader.face_alignment.FaceAlignModelLoader import FaceAlignModelLoader
from face_sdk.core.model_handler.face_alignment.FaceAlignModelHandler import FaceAlignModelHandler
from face_sdk.core.image_cropper.arcface_cropper.FaceRecImageCropper import FaceRecImageCropper
from face_sdk.core.model_loader.face_recognition.FaceRecModelLoader import FaceRecModelLoader
from face_sdk.core.model_handler.face_recognition.FaceRecModelHandler import FaceRecModelHandler

with open('face_sdk/config/model_conf.yaml') as f:
    model_conf = yaml.load(f,yaml.Loader)

if __name__ == '__main__':
    # common setting for all models, need not modify.
    model_path = 'face_sdk/models'

    # face detection model setting.
    scene = 'non-mask'
    model_category = 'face_detection'
    model_name =  model_conf[scene][model_category]
    logger.info('Start to load the face detection model...')
    try:
        faceDetModelLoader = FaceDetModelLoader(model_path, model_category, model_name)
        model, cfg = faceDetModelLoader.load_model()
        faceDetModelHandler = FaceDetModelHandler(model, 'cpu:0', cfg)
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
        faceAlignModelHandler = FaceAlignModelHandler(model, 'cpu:0', cfg)
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
        faceRecModelHandler = FaceRecModelHandler(model, 'cpu:0', cfg)
    except Exception as e:
        logger.error('Failed to load face recognition model.')
        logger.error(e)
        sys.exit(-1)
    else:
        logger.info('Success!')

    # read image and get face features.
    image_path = 'api_usage/test_images/test1.jpg'
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    face_cropper = FaceRecImageCropper()
    try:
        dets = faceDetModelHandler.inference_on_image(image)
        face_nums = dets.shape[0]
        if face_nums != 2:
            logger.info('Input image should contain two faces to compute similarity!')
        feature_list = []
        for i in range(face_nums):
            landmarks = faceAlignModelHandler.inference_on_image(image, dets[i])
            landmarks_list = []
            for (x, y) in landmarks.astype(np.int32):
                landmarks_list.extend((x, y))
            cropped_image = face_cropper.crop_image_by_mat(image, landmarks_list)
            feature = faceRecModelHandler.inference_on_image(cropped_image)
            feature_list.append(feature)
        score = np.dot(feature_list[0], feature_list[1])
        logger.info('The similarity score of two faces: %f' % score)
    except Exception as e:
        logger.error('Pipeline failed!')
        logger.error(e)
        sys.exit(-1)
    else:
        logger.info('Success!')