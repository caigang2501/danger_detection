# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-11-12 11:04:20 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-11-12 11:04:20 
"""
import os
import sys

import torch

from predictor import Predictor
from fire_detect.detect_fire_keras import DtcFire
from tools import dir_tools


def predect(frame_folder):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    predictor = Predictor(device=device)
    nohelmet_path = frame_folder.replace('/frames','/no_helmet')
    dir_tools.clear_dir(nohelmet_path)

    for file_name in os.listdir(frame_folder)[20:70]:
        img_path = frame_folder+file_name
        img = predictor.read_img(img_path)
        x = predictor.process_img(img)
        predictions = predictor.predict(x)
        n,img = predictor.display_boxes(img, predictions)
        if n>0:
            img.save(nohelmet_path+file_name)
            # img.show()

def my_detect_fire(frame_folder):
    fire_detector = DtcFire()
    dtc_fire_path = frame_folder.replace('/frames','/fired')
    dir_tools.clear_dir(dtc_fire_path)

    for file_name in os.listdir(frame_folder):
        file_path = frame_folder+file_name
        fired = fire_detector.detect(file_path)


if __name__ == '__main__':
    img_path = 'data/data_helmet/frames/'
    predect(img_path)
    # my_detect_helmet(img_path)