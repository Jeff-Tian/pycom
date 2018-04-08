import random

import time

__all__ = ['DataGenerator']


class DataGenerator(object):
    @staticmethod
    def randomize(ser):
        while True:
            data = random.random()
            if ser.isOpen():
                ser.write((str(data) + '\n').encode('utf-8'))

            time.sleep(0.2)
