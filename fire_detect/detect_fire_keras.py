import numpy as np
import os

import matplotlib.pyplot as plt

from keras.models import load_model
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input as inception_preprocess_input

class DtcFire:
    def __init__(self) -> None:
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'data/models/transfer_learned_model.h5')
        self.model = load_model(model_path)

    def detect(self,img_path:str):
        img = image.load_img(img_path, target_size=(224, 224, 3))
        img4save = image.load_img(img_path)
        processed_img = image.img_to_array(img)
        processed_img = np.expand_dims(processed_img, axis=0)
        processed_img = inception_preprocess_input(processed_img)
        predictions = self.model.predict(processed_img)[0]
        if predictions[0]>0.3:
            dtc_fire_path = img_path.replace('/frames','/fired')
            img4save.save(dtc_fire_path)

if __name__=='__main__':
    detector = DtcFire()
    fire_path = 'fire_images/2.jpg'
    nofire_paths = ['bird1.jpg','dog1.jpg','face1.jpg','mao1.jpg','tangwei.jpg','objdetect.png']
    detector.detect('data/output_frames/frame_0.jpg')
    # for i in range(15):
    #     detector.detect('data/fire_images/'+str(i)+'.jpg')

    # print('nofire:')
    # for path in nofire_paths:
    #     detector.detect('data/imgs/'+path)

# nbr_classes = 3
# result = [('classes_name', float(predictions[i]) * 100.0) for i in range(nbr_classes)]

# # sort the result by percentage
# result.sort(reverse=True, key=lambda x: x[1])

# # load image for displaying
# img = cv2.imread('fire_images/2.jpg')

# # transform into RGB
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# font = cv2.FONT_HERSHEY_COMPLEX

# # write class percentages on the image
# for i in range(nbr_classes):

#     # get the class and probability
#     (class_name, prob) = result[i]

#     textsize = cv2.getTextSize(class_name, font, 1, 2)[0]
#     textX = (img.shape[1] - textsize[0]) / 2
#     textY = (img.shape[0] + textsize[1]) / 2

#     # print max probability prediction on top of the image
#     if i == 0:
#         cv2.putText(img, class_name, (int(textX) - 100, int(textY)), font, 5, (255, 255, 255), 6, cv2.LINE_AA)

#     print("Class name: %s" % class_name)
#     print("Probability: %.2f%%" % prob)

# plt.imshow(img)
# plt.show()




# parser = argparse.ArgumentParser(description='Convolutional neural network for forest fire detection',
#                                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# parsed = parser.parse_args()