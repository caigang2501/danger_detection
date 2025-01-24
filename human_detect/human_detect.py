import numpy as np
import torch
from PIL import Image,ImageDraw
import os,sys

from torchvision.io.image import read_image
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import dir_tools,c_means

class HumanDetect:
    def __init__(self,points) -> None:
        # Step 1: Initialize model with the best available weights
        self.points= points[0]
        self.pit = points[1]
        self.weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
        self.model = fasterrcnn_resnet50_fpn_v2(weights=self.weights, box_score_thresh=0.9)
        self.model.eval()
        # Step 2: Initialize the inference transforms
        self.preprocess = self.weights.transforms()

    def point_in_quadrilateral(self,x, y):
        if len(self.points)!=8:
            return False
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

    def detect_human(self,img):
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
        return boxes
    
    def deal_result(self,path:str):
        img = read_image(path)
        boxes = self.detect_human(img)

        index_in_area,gathered = [],False
        foot_graph,foot_weith = [],[]
        for i,l in enumerate(boxes):
            x1,y1,x2,y2 = l
            if self.point_in_quadrilateral(x1,y2) and self.point_in_quadrilateral(x2,y2):
                index_in_area.append(i)
            if len(boxes)>3:
                foot_graph.append([((x1+x2)/2).detach().numpy(),y2.detach().numpy()])
                foot_weith.append(abs(x2-x1))
        if len(boxes)>3:
            idx = len(foot_weith)//4
            gather_valve = sum(foot_weith[idx:-idx])/(len(foot_weith)-2*idx)

            gathered = c_means.test_cmeans(np.array(foot_graph),1)/len(boxes)<3*gather_valve

        if len(index_in_area)>0:
            self.draw(path,img,boxes[index_in_area],'in_area',points=self.points)

        if gathered:
            self.draw(path,img,boxes,'gathered')
        return [len(index_in_area),1 if gathered else 0]


    def draw(self,path,img,boxes,folder,points=False):
        box = draw_bounding_boxes(img, boxes=boxes,
                                # labels=labels,
                                colors="red",
                                width=1)
        im = to_pil_image(box.detach())
        dtc_inarea_path = path.replace('frames/1',folder)
        draw = ImageDraw.Draw(im)
        if points:
            draw.polygon(points, outline="red")
        # img1.show()
        im.save(dtc_inarea_path)

if __name__=='__main__':
    points = ((0, 0, 60, 330, 480, 410, 500, 50),(300,300))
    detector = HumanDetect(points)
    frame_folder = "data/output_frames/frames/1/frame_0.jpg"
    detector.deal_result(frame_folder)