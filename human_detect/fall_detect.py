import torch,os
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

class FallDetector():
    def __init__(self):
        # image_processor = AutoImageProcessor.from_pretrained("rvv-karma/Human-Action-Recognition-VIT-Base-patch16-224")
        # model = AutoModelForImageClassification.from_pretrained("rvv-karma/Human-Action-Recognition-VIT-Base-patch16-224")
        custom_model_dir = os.path.join(os.getcwd(),'data/models')
        self.image_processor = AutoImageProcessor.from_pretrained("rvv-karma/Human-Action-Recognition-VIT-Base-patch16-224",cache_dir=custom_model_dir,local_files_only=True)
        self.model = AutoModelForImageClassification.from_pretrained("rvv-karma/Human-Action-Recognition-VIT-Base-patch16-224",cache_dir=custom_model_dir,local_files_only=True)

    def fall_detect(self,image_path):
        image = Image.open(image_path).convert("RGB")
        inputs = self.image_processor(image, return_tensors="pt")

        with torch.no_grad():
            logits = self.model(**inputs).logits
        predicted_label = logits.argmax(-1).item()
        action = self.model.config.id2label[predicted_label]
        if action in ['Sleeping']:
            image.save(image_path.replace('frames/1','falled'))
        return action


if __name__=='__main__':
    image_path = "data/output_frames/frames/1/frame_19.jpg"
    predictor = FallDetector()
    result = predictor.fall_detect(image_path)
    print(result)


