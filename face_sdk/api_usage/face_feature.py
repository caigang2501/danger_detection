"""
@author: JiXuan Xu, Jun Wang
@date: 20201016
@contact: jun21wangustc@gmail.com 
"""
import sys
import torch
sys.path.append('.')
import logging.config
logging.config.fileConfig("face_sdk/config/logging.conf")
logger = logging.getLogger('api')

import yaml
import cv2
import numpy as np

from face_sdk.core.model_loader.face_recognition.FaceRecModelLoader import FaceRecModelLoader
from face_sdk.core.model_handler.face_recognition.FaceRecModelHandler import FaceRecModelHandler

# torch.nn.Module.dump_patches = True

with open('face_sdk/config/model_conf.yaml') as f:
    model_conf = yaml.load(f,yaml.Loader)
    
if __name__ == '__main__':
    # common setting for all model, need not modify.
    model_path = 'models'

    # model setting, modified along with model
    scene = 'non-mask'
    model_category = 'face_recognition'
    model_name =  model_conf[scene][model_category]

    logger.info('Start to load the face recognition model...')
    # load model
    try:
        faceRecModelLoader = FaceRecModelLoader(model_path, model_category, model_name)
    except Exception as e:
        logger.error('Failed to parse model configuration file!')
        logger.error(e)
        sys.exit(-1)
    else:
        logger.info('Successfully parsed the model configuration file model_meta.json!')
        
    try:
        model, cfg = faceRecModelLoader.load_model()
        model = model.module.cpu() 

    except Exception as e:
        logger.error('Model loading failed!')
        logger.error(e)
        sys.exit(-1)
    else:
        logger.info('Successfully loaded the face recognition model!')

    # read image
    image_path = 'face_sdk/api_usage/temp/test1_cropped.jpg'
    image = cv2.imread(image_path)
    faceRecModelHandler = FaceRecModelHandler(model, 'cpu:0', cfg)

    try:
        feature = faceRecModelHandler.inference_on_image(image)
        print(feature.shape)
    except Exception as e:
        logger.error('Failed to extract facial features!')
        logger.error(e)
        sys.exit(-1)
    else:
        logger.info('Successfully extracted facial features!')

    np.save('face_sdk/api_usage/temp/test1_feature.npy', feature)
    np.load('face_sdk/api_usage/temp/test1_feature.npy')
