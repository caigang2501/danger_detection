import os,datetime,shutil,time,traceback
import multiprocessing as mp
from collections import deque
from typing import List
import torch
os.environ['TORCH_HOME']=os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/models')
# from fire_detect.detect_fire import DtcFire
from fire_detect.two_classfy import Predictor as fire_Predictor
from helmet_detect.predictor import Predictor
from human_detect.human_detect import HumanDetect
from human_detect.fall_detect import FallDetector
from face_sdk.api_usage.face_helper import FaceHelper

from video_processing import v2p_by_time
from tools import net_tool,dir_tools,ocr_tool

# def detect_fire_by_keras(minio_db,img_path):
#     fire_detector = DtcFire()
#     # detect fire
#     fired = fire_detector.detect(img_path)

#     if fired:
#         minio_db.update('detection/fired/'+str(datetime.date.today())+'/'+img_path.split('/')[-1],img_path)
minio_root = 'http://10.83.190.141:9000/zhgd/'
# sub_amount = 10
rec_accuracy = 0.2
minio_db = net_tool.MyMinio('zhgd')


def detect_human(t1,t2,points,frame_folder):
    predictor = HumanDetect(points)
    in_area_boxs,gathered_boxs = [],[]
    for i in range(t1,t2):
        file_name = f"frame_{i}.jpg"
        print('in_area_detect: '+file_name)
        file_path = frame_folder+file_name
        n_boxs = predictor.deal_result(file_path)
        in_area_boxs.append(n_boxs[0])
        gathered_boxs.append(n_boxs[1])
    return in_area_boxs,gathered_boxs

def filter_out(result_boxs):
    result_boxs.append(0)
    dq_img = deque()
    latest = 0
    result = []
    for num_img,boxs in enumerate(result_boxs):
        if latest!=boxs or len(dq_img)>20:
            if len(dq_img)>0 and latest!=0:
                result.append(f"frame_{dq_img[len(dq_img)//2]}.jpg")
            dq_img.clear()
        latest = boxs
        dq_img.append(num_img)
    
    return result

def deal_final_result(mg_dic,names,folder):
    facehelper = FaceHelper()
    paths_remote = [f'detection/{folder}/'+str(datetime.date.today())+'/'+file_name for file_name in names]
    paths_local = [mg_dic['frame_folder'][:-9]+f"/{folder}/"+file_name for file_name in names]

    recognized = []
    for i in range(len(names)):
        if folder=='no_helmet':
            recognizeds = facehelper.rec_face(paths_local[i],rec_accuracy)
        else:
            recognizeds = {}
        date = ocr_tool.get_video_date(paths_local[i])
        minio_db.update(paths_remote[i],paths_local[i])
        recognized.append({'names':recognizeds,'date':date,'path':minio_root+paths_remote[i]})
    
    return recognized

def deal_human_result(points,sub_amount,mg_dic):
    def gen_args(len_,sub_amount):
        parts = []
        for i in range(len_//sub_amount):
            parts.append((i*sub_amount,(i+1)*sub_amount,points,mg_dic['frame_folder']))
        parts.append((len_-len_%sub_amount,len_,points,mg_dic['frame_folder']))
        return parts
    
    len_ = len(os.listdir(mg_dic['frame_folder']))
    in_area_boxs,gathered_boxs = [],[]
    with mp.Pool(processes=min(len_//sub_amount+1,30)) as pool:
        args = gen_args(len_,sub_amount)
        result_boxs = pool.starmap(detect_human, args)
        [in_area_boxs.extend(box[0]) for box in result_boxs]
        [gathered_boxs.extend(box[1]) for box in result_boxs]
        
    print('in_area_boxs: ',in_area_boxs,
          '\ngathered_boxs: ',gathered_boxs)
    names_area = filter_out(in_area_boxs)
    names_gathered = filter_out(gathered_boxs)
    mg_dic['in_area'] = deal_final_result(mg_dic,names_area,'in_area')
    mg_dic['gathered'] = deal_final_result(mg_dic,names_gathered,'gathered')

    return

def detect_fire_by_torch(frame_folder:str):
    orderd_frame_folder = frame_folder.replace('/frames','/ordered_frames')
    fire_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/models/torch_firedtc_resnet50_3.pth')
    fire_predictor = fire_Predictor(fire_model_path)

    result = fire_predictor.predict_bypath(orderd_frame_folder[:-2])
    print('fire_result: ',result[1])
    result = [int(n) for n in result[1]]
    result.append(0)
    # print(type(result[0]),result)

    start = False
    warning = False
    filed_result = []
    destination_path = frame_folder[:-10]+'/fired/'
    for j,n in enumerate(result):
        if start:
            if n!=0 and not warning:
                if j-i>=2:
                    filed_result.append((i+j)//2)
                    file_name = f"frame_{(i+j)//2}.jpg"
                    shutil.copyfile(frame_folder+file_name,destination_path+file_name)
                    warning = True
            else:
                start = False
                warning = False
        else:
            if n>=1:
                i = j
                start = True
    
    print('filed_result',filed_result)
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

def deal_helmet_result(sub_amount,mg_dic):
    def gen_args(len_,sub_amount):
        parts = []
        for i in range(len_//sub_amount):
            parts.append((i*sub_amount,(i+1)*sub_amount,mg_dic['frame_folder']))
        parts.append((len_-len_%sub_amount,len_,mg_dic['frame_folder']))
        return parts

    len_ = len(os.listdir(mg_dic['frame_folder']))
    with mp.Pool(processes=min(len_//sub_amount+1,30)) as pool:
        args = gen_args(len_,sub_amount)
        result_boxs = pool.starmap(detect_helmet, args)
        result_boxs = [r for box in result_boxs for r in box]

    print('no_helmet_boxs: ',result_boxs)
    names_helmet = filter_out(result_boxs)
    mg_dic['no_helmet'] = deal_final_result(mg_dic,names_helmet,'no_helmet')
    return

def detect_fall(t1,t2,frame_folder):
    result_boxs = []
    predictor = FallDetector()
    for i in range(t1,t2):
        file_name = f"frame_{i}.jpg"
        print('falled detect: '+file_name)
        file_path = frame_folder+file_name
        result = predictor.fall_detect(file_path)
        result_boxs.append(result)
    return result_boxs

def deal_fall_result(sub_amount,mg_dic):
    def gen_args(len_,sub_amount):
        parts = []
        for i in range(len_//sub_amount):
            parts.append((i*sub_amount,(i+1)*sub_amount,mg_dic['frame_folder']))
        parts.append((len_-len_%sub_amount,len_,mg_dic['frame_folder']))
        return parts

    len_ = len(os.listdir(mg_dic['frame_folder']))
    with mp.Pool(processes=min(len_//sub_amount+1,30)) as pool:
        args = gen_args(len_,sub_amount)
        result_boxs = pool.starmap(detect_fall, args)
        result_boxs = [r for box in result_boxs for r in box]
    print('falled_result:',result_boxs)
    result_boxs = [1 if act in ['Sleeping'] else 0 for act in result_boxs]
    print('falled_result:',result_boxs)
    names_falled = filter_out(result_boxs)
    print('falled_result:',names_falled)
    mg_dic['falled'] = deal_final_result(mg_dic,names_falled,'falled')
    return

def main_fire(mg_dic):
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

def add_face(img_minio_path:str):
    facehelper = FaceHelper()
    try:
        img_name = img_minio_path.split('/')[-1]
        portrait_path = 'data/face/faces/'+img_name
        
        minio_db.down_load(img_minio_path.split('zhgd/')[-1],portrait_path)
    except:
        return 'wrong image path'
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
    video_path = "data/videos/temp_video.mp4"
    net_tool.download_by_requests(url,video_path)
    # minio_db.down_load(url.split('zhgd/')[-1],video_path)
    root = 'data/'+str(round(time.time()))
    root = 'data/'+'output_frames'
    frame_folder = root+'/frames/1/'
    ordered_frame_folder = root+'/ordered_frames/1/'
    dir_tools.mk_vedio_dirtree(root)
    v2p_by_time.extract_frames(video_path, frame_folder,second=frame_interval)
    v2p_by_time.extract_frames(video_path, ordered_frame_folder,second=frame_interval,ordered=True)

    with mp.Manager() as mg:
        mg_dic = mg.dict()
        mg_dic['frame_folder'] = frame_folder
        p_fire = mp.Process(target=main_fire,args=(mg_dic,))
        p_human = mp.Process(target=deal_human_result,args=(points,sub_amount,mg_dic))
        p_helmet = mp.Process(target=deal_helmet_result,args=(sub_amount,mg_dic))
        p_fall = mp.Process(target=deal_fall_result,args=(sub_amount,mg_dic))
        p_fire.start(),p_helmet.start(),p_human.start(),p_fall.start()
        p_fire.join(),p_helmet.join(),p_human.join(),p_fall.join()
        # p_helmet.start(),p_helmet.join()
        results = {
            'eara':ocr_tool.get_video_eara(frame_folder+'/frame_0.jpg'),
            'fired':mg_dic['fired'],
            'no_helmet':mg_dic['no_helmet'],
            'in_area':mg_dic['in_area'],
            'gathered':mg_dic['gathered'],
            'falled':mg_dic['falled']
        }
    # shutil.rmtree(root)
    return results

if __name__=='__main__':
    points = ((150, 200, 50, 300, 300, 300, 400, 200),(300,300))
    frame_interval = 5
    sub_amount = 15
    # points = (0,0)
    url = 'http://10.83.190.141:9000/zhgd/detection/test.mp4'
    r = main(url,points,frame_interval,sub_amount)
    print(r)
    # r = detect_fire_by_torch('data/output_frames/frames/1/')
    # print(r)
    # add_face('http://10.83.190.87:9000/zhgd/detection/faces/27/张三.jpg')
    # scp D:\workspace\hb_projects\danger_detection/danger_detection.zip user@10.83.190.141:caigang/
    # scp D:\workspace\hb_projects\danger_detection/main.py user@10.83.190.141:caigang/danger_detection/



