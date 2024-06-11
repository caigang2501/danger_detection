import multiprocessing

def init_process(data):
    global readonly_data
    readonly_data = data

def worker():
    print(f"Readonly data in process {multiprocessing.current_process().pid}: {readonly_data}")

if __name__ == "__main__":
    # 只读数据
    readonly_data = "Hello, world!"

    # 初始化 multiprocessing.Pool
    with multiprocessing.Pool(initializer=init_process, initargs=(readonly_data,)) as pool:
        # 启动一个子进程，并在其中执行 worker 函数
        pool.apply(worker)

    # 在主进程中打印只读数据
    print("Readonly data in main process:", readonly_data)


