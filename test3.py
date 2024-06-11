import os,shutil
import multiprocessing as mp

# os.mkdir('asdf')

a = [1]
print(a,id(a))

def test1():
    print('test1',a,id(a))

def test():
    global a
    a[0] = 2
    print('test',a,id(a))
    p = mp.Process(target=test1)
    p.start(),p.join()


if __name__=='__main__':
    test()








