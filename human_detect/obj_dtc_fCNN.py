import numpy as np
import torch
from PIL import Image
import os,sys

from torchvision.io.image import read_image
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helmet_detect import two_classfy
from tools import dir_tools
os.environ['TORCH_HOME']=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'data/models')

class HelmetDetect:
    def __init__(self) -> None:
        # Step 1: Initialize model with the best available weights
        self.weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
        self.model = fasterrcnn_resnet50_fpn_v2(weights=self.weights, box_score_thresh=0.9)
        self.model.eval()
        # Step 2: Initialize the inference transforms
        self.preprocess = self.weights.transforms()

    def detect(self,path:str):
        img = read_image(path)
        img1 = Image.open(path)
    # Step 3: Apply inference preprocessing transforms
        batch = [self.preprocess(img)]

        # Step 4: Use the model and visualize the prediction
        prediction = self.model(batch)[0]

        person_indices = [i for i, label in enumerate(prediction["labels"]) if label == 1]
        labels = [self.weights.meta["categories"][1] for i in person_indices]
        boxes = prediction["boxes"][person_indices]
        boxes = [[x1,y1,x2,y1+x2-x1] for [x1,y1,x2,y2] in boxes]
        if len(boxes)==0:
            return True

        save_path = 'data/objdetect/detected/1/'
        dir_tools.clear_dir(save_path)
        for i,l in enumerate(boxes):
            x1,y1,x2,y2 = l
            cropped_img = img1.crop((int(x1), int(y1), int(x2), int(y2)))
            cropped_img.save(save_path+str(i)+'.jpg')
        
        pred_val = two_classfy.predict_bypath('data/objdetect/detected')
        no_helmet = [[x1,y1,x2,y2] for i,[x1,y1,x2,y2] in enumerate(boxes) if pred_val[i]==0]
        boxes = torch.Tensor(no_helmet)
        labels = ['no helmet']*len(boxes)
        if len(no_helmet)==0:
            # img1.show()
            return True
        else:
            box = draw_bounding_boxes(img, boxes=boxes,
                                    labels=labels,
                                    colors="red",
                                    width=4)
            im = to_pil_image(box.detach())
            # data/output_frames/frames\\2.jpg'
            dtc_nohelmet_path = path.replace('/frames','/no_helmet') 
            im.save(dtc_nohelmet_path)
            img1.save(dtc_nohelmet_path.replace('.','org.'))
            
            im.show()
            return False

if __name__=='__main__':
    detector = HelmetDetect()

    frame_folder = "data/output_frames/frames"
    # for file_name in os.listdir(frame_folder):
    #     detector.detect(os.path.join(frame_folder, file_name))
    detector.detect(os.path.join(frame_folder, 'frame_40.jpg'))
    # pred_val = use_retrained_model.predict_bypath('data/objdetect/detected')
    # print(pred_val)