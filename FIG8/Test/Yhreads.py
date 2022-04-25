from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep, time
from multiprocessing import Pool
from multiprocessing import Process

from NeuralEmulator.VoltageSources.LinearSignal import StaticSource


def t1(obj):
    obj.setVoltage(5)


if __name__ == '__main__':
    v1Source = StaticSource(1)
    executor = ThreadPoolExecutor(max_workers=8)

    a = executor.submit(t1,v1Source)

    while a.done() is False:
        pass
    print(v1Source.getVoltage())

# def foo(t):
#     sleep(t)
#
#
# s = time()
# for x in range(8):
#     foo(0.5)
# print("Total {}".format(time() - s))
#
# task = []
# executor = ThreadPoolExecutor(max_workers=8)
#
# s = time()
#
# for x in range(8):
#     a = executor.submit(foo,0.5)
#     task.append(a)
#
# for t in task:
#     while t.done() is False:
#         pass
#
# print("Total {}".format(time() - s))
