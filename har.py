# Use a pipeline as a high-level helper
from transformers import pipeline
image_path = "data/train/fall/fall000.jpg"

def test1():
    global image_path
    # pipe = pipeline("image-classification", model="DrishtiSharma/finetuned-ViT-human-action-recognition-v1")
    pipe = pipeline("image-classification", "rvv-karma/Human-Action-Recognition-VIT-Base-patch16-224")
    for i in range(10):
        image_path = image_path.replace('000','00'+str(i))
        results = pipe(image_path)
        best_prediction = max(results, key=lambda x: x["score"])
        print(best_prediction)
    # for result in results:
    #     print(f"Label: {result['label']}, Score: {result['score']}")

test1()
