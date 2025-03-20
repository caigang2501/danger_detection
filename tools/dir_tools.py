import os,shutil,time

def clear_dir(path):
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            clear_dir(file_path)

def mk_vedio_dirtree(root):
    if os.path.exists(root):
        shutil.rmtree(root)
    os.mkdir(root)
    os.mkdir(root+'/fired')
    os.mkdir(root+'/frames')
    os.mkdir(root+'/frames/1')
    os.mkdir(root+'/in_area')
    os.mkdir(root+'/no_helmet')
    os.mkdir(root+'/gathered')
    os.mkdir(root+'/falled')


if __name__=='__main__':
    mk_vedio_dirtree('data/'+'output_frames')