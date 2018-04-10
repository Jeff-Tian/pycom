import threading

from time import gmtime
from time import strftime

import serial

import numpy as np
import matplotlib.pyplot as plt

__all__ = ['DataVisualizer']


class DataVisualizer:
    def __init__(self, ser):
        self.file_name = strftime('%Y-%m-%d %H%M%S.csv', gmtime())
        self.ser = ser

    def start(self):
        thread = threading.Thread(target=self.display_data_from_port, args=[])
        thread.daemon = True
        thread.start()

    def display_data_from_port(self):
        while self.ser.isOpen():
            n = self.ser.inWaiting()
            if n > 0:
                response = self.ser.readline().decode('utf-8')
                print('response = ', strftime('%Y-%m-%d %H:%M:%S', gmtime()), response)
                self.append_data_to_file(response)

    def append_data_to_file(self, data=None):
        with open(self.file_name, 'a') as data_file:
            data_file.writelines(['{}, {}'.format(strftime('%Y-%m-%d %H:%M:%S', gmtime()), data)])

    def write_data_to_file(self):
        with open(self.file_name, 'w') as data_file:
            data_file.writelines(['{}, {}'.format('timestamp', 'data'), '\n'])
