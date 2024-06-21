import os,datetime,shutil,time
import multiprocessing as mp
from collections import deque
from typing import List
import torch
os.environ['TORCH_HOME']=os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/models')
# from fire_detect.detect_fire import DtcFire
from fire_detect.two_classfy import Predictor as fire_Predictor
from helmet_detect.predictor import Predictor
from area_detect.area_detect import InAreaDetect
from face_sdk.api_usage.face_helper import FaceHelper

from video_processing import v2p_by_time
from tools import net_tool,dir_tools,ocr_tool

# def detect_fire_by_keras(minio_db,img_path):
#     fire_detector = DtcFire()
#     # detect fire
#     fired = fire_detector.detect(img_path)

#     if fired:
#         minio_db.update('detection/fired/'+str(datetime.date.today())+'/'+img_path.split('/')[-1],img_path)
minio_root = 'http://10.83.190.87:9000/zhgd/'
# sub_amount = 10
rec_accuracy = 0.15


def detect_in_area(t1,t2,points,frame_folder):
    predictor = InAreaDetect(points)
    result_boxs = []
    for i in range(t1,t2):
        file_name = f"frame_{i}.jpg"
        print('in_area_detect: '+file_name)
        file_path = frame_folder+file_name
        n_boxs = predictor.detect(file_path)
        result_boxs.append(n_boxs)
    return result_boxs

def deal_area_result(points,sub_amount,frame_folder):
    def gen_args(len_,sub_amount):
        parts = []
        for i in range(len_//sub_amount):
            parts.append((i*sub_amount,(i+1)*sub_amount,points,frame_folder))
        parts.append((len_-len_%sub_amount,len_,points,frame_folder))
        return parts
    
    len_ = len(os.listdir(frame_folder))
    with mp.Pool(processes=min(len_//sub_amount+1,30)) as pool:
        args = gen_args(len_,sub_amount)
        args.append(frame_folder)
        result_boxs = pool.starmap(detect_in_area, args)
        result_boxs = [item for row in result_boxs for item in row]
    print(result_boxs)

    dq_n = 0
    dq_img = deque()
    prev,mid = 0,0
    prev_img,mid_img = 0,0
    result = []
    # ordered by string,not the menu order
    for num_img,n_boxs in enumerate(result_boxs):
        file_name = f"frame_{num_img}.jpg"
        print('in_area_detect: '+file_name)

        if prev==n_boxs and prev!=mid:
            mid = n_boxs
            mid_img = num_img
        else:
            if dq_n!=prev or len(dq_img)>20:
                if len(dq_img)>0 and dq_n!=0:
                    result.append(f"frame_{dq_img[len(dq_img)//2]}.jpg")
                dq_img.clear()
            dq_n = prev
            dq_img.append(prev_img)
            prev = mid
            prev_img = mid_img
            mid = n_boxs
            mid_img = num_img

    print(result)
    return result


def detect_fire_by_torch(frame_folder):
    fire_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/models/torch_firedtc_resnet50.pth')
    fire_predictor = fire_Predictor(fire_model_path)

    result = fire_predictor.predict_bypath(frame_folder[:-2])
    result = [int(n) for n in result[1]]
    result.append(0)
    # print(type(result[0]),result)

    len_one = 3
    start = False
    filed_result = []
    destination_path = frame_folder[:-10]+'/fired/'
    for j,n in enumerate(result):
        if start:
            if n==0:
                if j-i>=len_one:
                    filed_result.append((i+j)//2)
                    file_name = f"frame_{(i+j)//2}.jpg"
                    shutil.copyfile(frame_folder+file_name,destination_path+file_name)
                start = False
        else:
            if n==1:
                i = j
                start = True
    
    # filed_names = [file_name for i,file_name in enumerate(os.listdir(data_root+'/1')) if i in filed_result]
    filed_names = [f"frame_{n}.jpg" for n in filed_result]
    return filed_names
    

def detect_helmet(t1,t2,frame_folder):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    predictor = Predictor(device=device)
    result_boxs = []
    nohelmet_path = frame_folder[:-10]+'/no_helmet/'

    for i in range(t1,t2):
        file_name = f"frame_{i}.jpg"
        print('in_helmet_detect: '+file_name)
        file_path = frame_folder+file_name

        curr_img = predictor.read_img(file_path)
        x = predictor.process_img(curr_img)
        predictions = predictor.predict(x)
        boxs,curr_img = predictor.display_boxes(curr_img, predictions)
        result_boxs.append(boxs)
        if boxs>0:
            curr_img.save(nohelmet_path+file_name)
    return result_boxs

def deal_helmet_result(sub_amount,frame_folder):
    def gen_args(len_,sub_amount):
        parts = []
        for i in range(len_//sub_amount):
            parts.append((i*sub_amount,(i+1)*sub_amount,frame_folder))
        parts.append((len_-len_%sub_amount,len_,frame_folder))
        return parts

    len_ = len(os.listdir(frame_folder))
    with mp.Pool(processes=min(len_//sub_amount+1,30)) as pool:
        args = gen_args(len_,sub_amount)
        result_boxs = pool.starmap(detect_helmet, args)
        result_boxs = [item for row in result_boxs for item in row]

    dq_n = 0
    dq_img = deque()
    prev,mid = 0,0
    prev_img,mid_img = 0,0
    result = []

    # ordered by string,not the menu order
    for num_img,boxs in enumerate(result_boxs):
        if prev==boxs and prev!=mid and False:
            mid = boxs
            mid_img = num_img
        else:
            if dq_n!=prev or len(dq_img)>20:
                if len(dq_img)>0 and dq_n!=0:
                    result.append(f"frame_{dq_img[len(dq_img)//2]}.jpg")
                dq_img.clear()
            dq_n = prev
            dq_img.append(prev_img)
            prev = mid
            prev_img = mid_img
            mid = boxs
            mid_img = num_img

    print(result_boxs)
    print(result)
    return result

def main_fire(mg_dic):
    minio_db = net_tool.MyMinio('zhgd')
    names_fired = detect_fire_by_torch(mg_dic['frame_folder'])
    paths_fired_remote = ['detection/fired/'+str(datetime.date.today())+'/'+file_name for file_name in names_fired]
    paths_fired_local = [mg_dic['frame_folder'][:-10]+"/fired/"+file_name for file_name in names_fired]
    fired_info = []
    for i in range(len(names_fired)):
        date = ocr_tool.get_video_date(paths_fired_local[i]) 
        minio_db.update(paths_fired_remote[i],paths_fired_local[i])
        fired_info.append({'date':date,'path':minio_root+paths_fired_remote[i]})
    mg_dic['fired'] = fired_info
    return fired_info

def main_helmet(sub_amount,mg_dic):
    facehelper = FaceHelper()
    minio_db = net_tool.MyMinio('zhgd')
    names_helmet = deal_helmet_result(sub_amount,mg_dic['frame_folder'])
    paths_helmet_remote = ['detection/no_helmet/'+str(datetime.date.today())+'/'+file_name for file_name in names_helmet]
    paths_helmet_local = [mg_dic['frame_folder'][:-9]+"/no_helmet/"+file_name for file_name in names_helmet]

    recognized_pairs = []
    for i in range(len(names_helmet)):
        recognizeds = facehelper.rec_face(paths_helmet_local[i],rec_accuracy)
        date = ocr_tool.get_video_date(paths_helmet_local[i]) 
        minio_db.update(paths_helmet_remote[i],paths_helmet_local[i])
        recognized_pairs.append({'names':recognizeds,'date':date,'path':minio_root+paths_helmet_remote[i]})
    mg_dic['no_helmet'] = recognized_pairs
    return recognized_pairs

def main_area(points,sub_amount,mg_dic):
    facehelper = FaceHelper()
    if len(points)==8:
        minio_db = net_tool.MyMinio('zhgd')
        names_area = deal_area_result(points,sub_amount,mg_dic['frame_folder'])
        paths_area_remote = ['detection/in_area/'+str(datetime.date.today())+'/'+file_name for file_name in names_area]
        paths_area_local = [mg_dic['frame_folder'][:-9]+"/in_area/"+file_name for file_name in names_area]

        recognized_pairs = []
        for i in range(len(names_area)):
            recognizeds = facehelper.rec_face(paths_area_local[i],rec_accuracy)
            date = ocr_tool.get_video_date(paths_area_local[i])
            minio_db.update(paths_area_remote[i],paths_area_local[i])
            recognized_pairs.append({'names':recognizeds,'date':date,'path':minio_root+paths_area_remote[i]})
        mg_dic['in_area'] = recognized_pairs
        return recognized_pairs
    else:
        mg_dic['in_area'] = []
        return []

def add_face(img_minio_path:str):
    try:
        img_name = img_minio_path.split('/')[-1]
        portrait_path = 'data/face/faces/'+img_name
        minio_db = net_tool.MyMinio('zhgd')
        minio_db.down_load(img_minio_path.split('zhgd/')[-1],portrait_path)
    except:
        return 'wrong image path'
    facehelper = FaceHelper()
    facehelper.add_face(portrait_path)
    return 'ssucced'

def remove_face(name:str):
    try:
        os.remove('data/face/features/name.npy'.replace('name',name))
    except:
        return 'no such name'
    else:
        return 'ssucced'

def all_face():
    names = []
    for file_name in os.listdir('data/face/features'):
        names.append(file_name.split('.')[0])
    return names

def main(url:str,points:List,frame_interval,sub_amount):
    minio_db = net_tool.MyMinio('zhgd')
    video_path = "data/videos/temp_video.mp4"

    try:
        net_tool.download_by_requests(url,video_path)
    except Exception as e:
        return f'download video failed: {e}'
    # minio_db.down_load(url.split('zhgd/')[-1],video_path)
    root = 'data/'+str(round(time.time()))
    frame_folder = root+'/frames/1/'
    dir_tools.mk_vedio_dirtree(root)
    v2p_by_time.extract_frames(video_path, frame_folder,second=frame_interval)


    with mp.Manager() as mg:
        mg_dic = mg.dict()
        mg_dic['frame_folder'] = frame_folder
        p_fire = mp.Process(target=main_fire,args=(mg_dic,))
        p_area = mp.Process(target=main_area,args=(points,sub_amount,mg_dic))
        p_helmet = mp.Process(target=main_helmet,args=(sub_amount,mg_dic))
        p_fire.start(),p_area.start(),p_helmet.start()
        p_fire.join(),p_area.join(),p_helmet.join()

        results = { 'eara':ocr_tool.get_video_eara(frame_folder+'/frame_0.jpg'),
                    'fired':mg_dic['fired'],
                    'no_helmet':mg_dic['no_helmet'],
                    'in_area':mg_dic['in_area']}
        
        print(results)
    # shutil.rmtree(root)
    return results

if __name__=='__main__':
    frame_interval = 3
    # points = (0, 0, 60, 330, 480, 410, 500, 50)
    sub_amount = 10
    points = (0,0)
    url = 'http://10.83.190.87:9000/zhgd/test.mp4'
    main(url,points,frame_interval,sub_amount)
    # add_face('http://10.83.190.87:9000/zhgd/detection/faces/27/张三.jpg')




