import os,shutil,time

def clear_dir(path):
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            clear_dir(file_path)

def mk_vedio_dirtree(root):
    os.mkdir(root)
    os.mkdir(root+'/fired')
    os.mkdir(root+'/frames')
    os.mkdir(root+'/frames/1')
    os.mkdir(root+'/in_area')
    os.mkdir(root+'/no_helmet')
    os.mkdir(root+'/gathered')



if __name__=='__main__':
    root = 'data/'+str(round(time.time()))
    mk_vedio_dirtree(root)
    time.sleep(4)
    shutil.rmtree(root)