# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-11-11 19:20:06 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-11-11 19:20:06 
"""
import os

import torch
from PIL import Image, ImageDraw, ImageFont

from helmet_detect.model import fasterrcnn_resnet_fpn
from helmet_detect.transforms import get_transforms



class Predictor(object):
    def __init__(self, weights_path=None, backbone='resnet50', device='cpu'):
        self.weights_path = weights_path
        if self.weights_path is None:
            self.weights_path = 'data/models/best_model.pt'
        self.backbone = backbone
        self.device = device
        self.model = fasterrcnn_resnet_fpn(resnet_name=backbone)
        self.model.load_state_dict(torch.load(
            self.weights_path, map_location=torch.device(device)))
        self.model = self.model.to(device)
        self.model.eval()

    def read_img(self, img_path):
        return Image.open(img_path)

    def process_img(self, img):
        transforms = get_transforms(False)
        img = img.convert('RGB')
        img, _ = transforms(img, None)
        x = img.to(self.device)
        return x

    def predict(self, x):
        with torch.no_grad():
            predictions = self.model([x])
            predictions = {k: v.to('cpu').data.numpy()
                           for k, v in predictions[0].items()}
        return predictions

    def display_boxes(self, img, predictions, score_thresh=0.9):
        boxes_count = 0
        bd = 30
        boxes, scores = predictions['boxes'], predictions['scores']
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('data/style/font.ttf', size=20)
        for i, cur_bbox in enumerate(boxes):
            if scores[i] < score_thresh:
                continue
            if cur_bbox[0]>5 and cur_bbox[1]>10:
                boxes_count += 1
                draw.rectangle(cur_bbox, outline=(255, 0, 0), width=1)
                left_corner = (cur_bbox[0]+4, cur_bbox[1]+4)
                # draw.text(left_corner, 'score: {:.4f}'.format(
                #     scores[i]), fill='red', font=font)
        return boxes_count,img
 
if __name__=='__main__':
    predictor = Predictor()
    # img = predictor.read_img('demo/demo2.jpg')
    # x = predictor.process_img(img)
    # predictions = predictor.predict(x)
    # n,result_img = predictor.display_boxes(img,predictions)
    # result_img.show()


