import os,socket
from PIL import Image
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import pytesseract,easyocr

if 'WINDOWS' in socket.gethostname():
    tesser_path = 'data/Tesseract-OCR/tesseract.exe'
else:
    tesser_path = '../usr/bin/tesseract'

def ocr_tesseract(img_path):
    image = Image.open(img_path)
    pytesseract.pytesseract.tesseract_cmd = tesser_path
    result = pytesseract.image_to_string(image,lang='chi_sim+eng')
    return result

def ocr_easy(img_path):
    reader = easyocr.Reader(['ch_sim','en'],model_storage_directory = 'data/models')
    result = reader.readtext(img_path)
    return result

def get_video_date(img_path):
    try:
        img = Image.open(img_path)
        width, height = img.size
        img_date = img.crop((0,0,width//2,height//5))
        temp_path = 'data/videos/crop4ocr_date.jpg'
        img_date.save(temp_path)
        pytesseract.pytesseract.tesseract_cmd = tesser_path
        date = pytesseract.image_to_string(img_date,lang='chi_sim+eng')

        # adjust date read mistake
        date = date.replace(' ','')
        date = date.strip()
        i,j = date.index('年'),date.index('月')
        if j-i>3:
            date = date[:i+1]+date[j-2:j]+date[j:]
        if date[5]>'2':
            date = date[:5]+'0'+date[6:]
        if date[-8]>'2':
            date = date[:-8]+'0'+date[-7:]
        if date[-5]>'6':
            date = date[:-5]+'0'+date[-4:]
        if date[-2]>'6':
            date = date[:-2]+'0'+date[-1]

    except Exception as e:
        print(f'ocr wrong: {e}')
        return "no date info"
    return date

def get_video_eara(img_path):
    try:
        img = Image.open(img_path)
        width, height = img.size
        img_eara = img.crop((width//2,height - height//5,width,height))
        temp_path = 'data/videos/crop4ocr.jpg'
        img_eara.save(temp_path)

        eara = ocr_easy(temp_path)
        eara = eara[0][1]
    except Exception as e:
        print(f'ocr wrong: {e}')
        return "no eara info"
    return eara

def test1(img_path):
    img = Image.open(img_path)
    width, height = img.size
    img_date = img.crop((0,0,500,50))
    img_eara = img.crop((width-300,height-50,width,height))
    # img_date.show()

    pytesseract.pytesseract.tesseract_cmd = 'data/Tesseract-OCR/tesseract.exe'
    tes_date = pytesseract.image_to_string(img_date,lang='chi_sim+eng')
    tes_eara = pytesseract.image_to_string(img_eara,lang='chi_sim+eng')
    print(tes_date,tes_eara)

    # reader = easyocr.Reader(['ch_sim','en'],model_storage_directory = 'data/models')
    # temp_path = 'data/videos/crop4ocr.jpg'
    # img_date.save(temp_path)
    # easy_date = reader.readtext(temp_path)
    # img_eara.save(temp_path)
    # easy_eara = reader.readtext(temp_path)
    # print(easy_date,easy_eara)

def final_test(img_path):
    result1 = get_video_date(img_path)
    result2 = get_video_eara(img_path)

    print(result1,result2)


if __name__=='__main__':
    img_path = 'data/output_frames/frames/1/frame_0.jpg'
    # test1(img_path)
    # final_test(img_path)
    ocr_easy(img_path)








