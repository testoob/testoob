def other_thread_func():
    b = 1

def multi_thread_func():
    import threading
    th = threading.Thread(target=other_thread_func)
    th.start()
    th.join()
