#!/usr/bin/env python3
from multiprocessing import Process

def test_function(proc_number):
    print('hello', proc_number)

if __name__ == '__main__':
    processes = []
    for i in range(0, 10000):
        processes.append(Process(target=test_function, args=(i,)))
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print("Finished!")

