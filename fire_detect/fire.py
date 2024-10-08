import os
from transformers import pipeline

os.environ["TRANSFORMERS_CACHE"] = "/your/custom/cache/directory"

# default model path: C:\Users\EDY\.cache\huggingface\hub\
pipe = pipeline("image-classification", model="EdBianchi/vit-fire-detection")


image_path = 'data/train/fire/1/5.jpg'

results = pipe(image_path)

for result in results:
    print(f"Label: {result['label']}, Score: {result['score']}")
    