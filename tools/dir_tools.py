import os

def clear_dir(path):
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            clear_dir(file_path)

if __name__=='__main__':
    save_path = 'train copy'
    clear_dir(save_path)