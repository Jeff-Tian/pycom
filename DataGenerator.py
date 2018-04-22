import random

import time

__all__ = ['DataGenerator']


class DataGenerator(object):
    @staticmethod
    def randomize(gui, ser):
        while True:
            data = random.random()
            gui.change_status(data)

            gui.frighten_device.append_data_to_file(data)

            time.sleep(0.2)
