import threading

from time import gmtime, sleep
from time import strftime

from matplotlib import dates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

import pandas as pd

from  PPI import *
from helper import hex_decode

__all__ = ['FrightenDevice']


class FrightenDevice:
    def __init__(self, gui):
        self.file_name = strftime('%Y-%m-%d %H%M%S.csv', gmtime())
        self.gui = gui
        self.window = gui.window
        self.ser = gui.ser
        self.index = 0
        self.x = []
        self.y = []
        self.first_write = True

        self.fig = Figure(figsize=(self.window.winfo_screenwidth(), 6))
        self.chart = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack()

    def start(self):
        # thread = threading.Thread(target=self.display_data_from_port, args=[])
        # thread.daemon = True
        # thread.start()

        thread = threading.Thread(target=self.ask_gravity_data, args=[])
        thread.daemon = True
        thread.start()
        self.gui.change_status('开始询问重力数据……')

    def handle_gravity_data(self, data):
        gravity_data = PPI.parse_gravity_data(data)
        self.gui.change_status('{}：{}g'.format(hex_decode(data), gravity_data))
        self.plot_gravity_data(gravity_data)

    def ask_gravity_data(self):
        while self.ser.isOpen():
            self.issue_command(bytearray([0xAA, 0x4A, 0x4C, 0x04, 0x00, 0x86, 0x0F, 0x00, 0x01]),
                               self.handle_gravity_data)

    def issue_command(self, command, expected_response):
        if self.ser.isOpen:
            self.gui.change_status('发送命令：{}'.format(hex_decode(command)))
            self.last_command = command
            self.ser.write(command)
            self.get_response(expected_response)
        else:
            self.gui.change_status('不能发送命令，COM 端口没有打开！')

    def plot(self, data):
        try:
            self.index += 1
            self.x.append(self.index)
            self.y.append(data)

            self.chart.scatter(self.x, self.y, color='blue')
            self.canvas.draw()
        except ValueError:
            pass

    def plot_gravity_data(self, data):
        try:
            self.index += 1
            self.x.append(self.index)
            self.y.append(data)

            self.chart.plot(self.x, self.y, 'bo--')
            self.chart.set_xticklabels(self.x, rotation=17)
            self.chart.set_title(label=u'PP = {}'.format(np.average(self.y)))
            self.canvas.draw()
        except ValueError:
            pass

    def plot_csv(self, csv_file):
        data = pd.read_csv(csv_file, '\, *', engine='python')
        self.x = data.timestamp
        self.y = data.data
        self.chart.plot(self.x, self.y, 'bo--')
        self.chart.set_xticklabels(self.x, rotation=17)
        self.chart.set_title(label=u'PP = {}'.format(np.average(self.y)))
        self.canvas.draw()

    def append_data_to_file(self, data=None):
        if self.first_write:
            self.write_file()
            self.first_write = False

        with open(self.file_name, 'a') as data_file:
            data_file.writelines(
                ['{},{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'), data), '\n'])

    def write_file(self):
        with open(self.file_name, 'w') as data_file:
            data_file.writelines(['{},{}'.format('timestamp', 'data'), '\n'])

    def get_response(self, expected_response=None):
        while True:
            n = self.ser.inWaiting()
            self.gui.change_status('等待命令 {} 的回复……'.format(hex_decode(self.last_command)))
            if n > 0:
                data = self.ser.read(n)

                if expected_response is None:
                    self.gui.change_status('收到数据：{}'.format(hex_decode(data)))
                elif callable(expected_response):
                    expected_response(data)
                elif data == expected_response:
                    self.gui.change_status('命令执行成功。{}'.format(hex_decode(data)))
                else:
                    self.gui.change_status('命令执行失败。{}{}{}{}'.format('命令返回：', hex_decode(data), ' 期待：',
                                                                    hex_decode(expected_response)))

                self.window.event_generate('<<data_received>>', when='tail', data=hex_decode(data))
                break
            else:
                sleep(0.1)
