







import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time

"""
t1 = time.time()
plt.figure()
t2 = time.time()
print(t2 - t1)
ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))  
ts = np.exp(ts.cumsum())  
ts.plot(logy=True)
t3 = time.time()
print(t3 - t2)
plt.show()
"""

"""
f_obj = open('H:/osdr/code/recv.bin', "rb")
data = f_obj.read()
f_obj.close()

arr = np.frombuffer(data, dtype=np.int8)

plt.figure(1)


t1 = time.time()
plt.plot(arr)
t2 = time.time()


'''
t1 = time.time()
ts = pd.Series(arr)
ts.plot()
t2 = time.time()
'''

print(t2 - t1)
plt.show()
plt.close()
t3 = time.time()
print(t3 - t2)
"""


import threading
import multiprocessing as mp
import time
import queue



def func1(share, queue):
    for i in range(10):
        if (share["fd"] == None):
            print("error")
        else:
            print(share["fd"])
        time.sleep(1)
        #res = queue.get()
        #print(res)


def func2(share, queue):
    for i in range(10):
        time.sleep(1)
        share["fd"] = i
        #queue.put(i)


if __name__ == "__main__":
    mp.set_start_method('spawn')

    share = mp.Manager().dict()
    share["fd"] = None
    #fd = mp.Value("d", None)
    c_queue = mp.Queue()
    """
    process1 = mp.Process(target = func1, args=(fd, c_queue))
    process1.start()

    process2 = mp.Process(target = func2, args=(fd, c_queue))
    process2.start()
    """

    thread_ui_set = threading.Thread(target = func1, args = (share, c_queue))
    thread_ui_set.start()   

    thread_ui_set = threading.Thread(target = func2, args = (share, c_queue))
    thread_ui_set.start()       



"""
import multiprocessing as mp

def foo(q):
    q.put('hello')

if __name__ == '__main__':
    mp.set_start_method('spawn')
    q = mp.Queue()
    p = mp.Process(target=foo, args=(q,))
    p.start()
    print(q.get())
    p.join()
"""

