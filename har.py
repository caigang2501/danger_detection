# Use a pipeline as a high-level helper
from transformers import pipeline

# sleeping sitting fighting dancing running taxting cycling using_laptop listen_music 
pipe = pipeline("image-classification", model="DrishtiSharma/finetuned-ViT-human-action-recognition-v1")

image_path = "data/train/fall/fall033.jpg"

results = pipe(image_path)

for result in results:
    print(f"Label: {result['label']}, Score: {result['score']}")


