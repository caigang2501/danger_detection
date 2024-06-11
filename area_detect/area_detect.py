import numpy as np
import torch
from PIL import Image,ImageDraw
import os,sys

from torchvision.io.image import read_image
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import dir_tools

class InAreaDetect:
    def __init__(self,points) -> None:
        # Step 1: Initialize model with the best available weights
        self.points= points
        self.weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
        self.model = fasterrcnn_resnet50_fpn_v2(weights=self.weights, box_score_thresh=0.9)
        self.model.eval()
        # Step 2: Initialize the inference transforms
        self.preprocess = self.weights.transforms()

    def point_in_quadrilateral(self,x, y):
        x1, y1, x2, y2, x3, y3, x4, y4 = self.points
        def cross_product(ax, ay, bx, by, cx, cy):
            return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

        # 计算四个边的向量及叉乘结果
        cross1 = cross_product(x1, y1, x2, y2, x, y)
        cross2 = cross_product(x2, y2, x3, y3, x, y)
        cross3 = cross_product(x3, y3, x4, y4, x, y)
        cross4 = cross_product(x4, y4, x1, y1, x, y)

        # 检查点是否在四边形内部
        if (cross1 > 0 and cross2 > 0 and cross3 > 0 and cross4 > 0) or \
        (cross1 < 0 and cross2 < 0 and cross3 < 0 and cross4 < 0):
            return True
        else:
            return False    

    def detect(self,path:str):
        img = read_image(path)
    # Step 3: Apply inference preprocessing transforms
        batch = [self.preprocess(img)]

        # Step 4: Use the model and visualize the prediction
        prediction = self.model(batch)[0]
        # print(prediction)

        person_indices = [i for i, label in enumerate(prediction["labels"]) if label == 1]
        labels = [self.weights.meta["categories"][1] for i in person_indices]
        boxes = prediction["boxes"][person_indices]
        # boxes[0] = torch.FloatTensor([0,0,50,50])

        # 截取检测到的区域并保存
        # save_path = 'data/objdetect/detected/1/'
        # dir_tools.clear_dir(save_path)
        # for i,l in enumerate(boxes):
        #     x1,y1,x2,y2 = l
        #     cropped_img = img1.crop((int(x1), int(y1), int(x2), int(y2)))
        #     cropped_img.save(save_path+str(i)+'.jpg')
        index_in_area = []
        for i,l in enumerate(boxes):
            x1,y1,x2,y2 = l
            if self.point_in_quadrilateral(x1,y2) and self.point_in_quadrilateral(x2,y2):
                index_in_area.append(i)
        if len(index_in_area)>0:
            box = draw_bounding_boxes(img, boxes=boxes[index_in_area],
                                    # labels=labels,
                                    colors="red",
                                    width=1)
            im = to_pil_image(box.detach())
            dtc_inarea_path = path.replace('frames/1','in_area')
            im.save(dtc_inarea_path)

            # 在图像上绘制多边形区域
            img1 = Image.open(dtc_inarea_path)
            draw = ImageDraw.Draw(img1)
            draw.polygon(self.points, outline="red")
            # img1.show()
            img1.save(dtc_inarea_path)
            
        return len(index_in_area)

if __name__=='__main__':
    points = (0, 0, 60, 330, 480, 410, 500, 50)
    detector = InAreaDetect(points)

    frame_folder = "data/output_frames/frames/1"
    detector.detect(os.path.join(frame_folder, 'frame_100002.jpg'))