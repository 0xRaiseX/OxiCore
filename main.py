import multiprocessing
from multiprocessing import Queue, Lock
import time
from stream_data import start_process
from stream1 import start_stream_1
from stream2 import start_stream_2
from stream3list import start_stream_3
from create_order import start_load


if __name__ == '__main__':

    queue = Queue(maxsize=10)
    queue1 = Queue(maxsize=1)
    queue2 = Queue(maxsize=1)
    queue3 = Queue(maxsize=1)


    process1 = multiprocessing.Process(target=start_process, args=(queue,queue1,queue2,queue3))
    process1.start()
    try:
        while True:
            get = queue1.get()
            if get:
                start_load(get)
                break
    except Exception as e:
        process1.terminate()
        process1.join()
        print('Ошибка запуска', e)
        raise SystemExit

    process2 = multiprocessing.Process(target=start_stream_1, args=(queue1,))
    process2.start()

    process3 = multiprocessing.Process(target=start_stream_2, args=(queue2,))
    process3.start()

    process4 = multiprocessing.Process(target=start_stream_3, args=(queue3,))
    process4.start()


    try:
        while True:
            pass
    except KeyboardInterrupt:

        process1.terminate()
        process2.terminate()
        process3.terminate()
        process4.terminate()

        process1.join()
        process2.join()
        process3.join()
        process4.join()