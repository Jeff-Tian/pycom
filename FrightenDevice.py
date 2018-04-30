import threading

from time import gmtime, sleep
from time import strftime
from tkinter import messagebox

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

__all__ = ['FrightenDevice', 'commands', 'command_responses']

commands = {
    'login': bytearray(
        [0xAA, 0x4A, 0x4C, 0x0C, 0x00, 0x81, 0x02, 0x00, 0x01, 0x11, 0x11, 0x22, 0x22, 0x02, 0x04, 0x01, 0x01]),
    'start_experiment': bytearray([0xAA, 0x4A, 0x4C, 0x05, 0x00, 0x84, 0x02, 0x00, 0x01, 0x47]),
    'end_experiment': bytearray([0xAA, 0x4A, 0x4C, 0x05, 0x00, 0x84, 0x02, 0x00, 0x01, 0x4F]),
    'beep': bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x34, 0x05, 0x00, 0x00]),
    'beep_on_off': bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x42, 0x88]),
    'light_on_off': bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x4C, 0x88]),
    'electricity_on_off': bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x45, 0x88]),
    'gravity_data': bytearray([0xAA, 0x4A, 0x4C, 0x04, 0x00, 0x86, 0x0F, 0x00, 0x01]),
    'flash_on': bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x45, 0x11]),
}

command_responses = {
    'login': bytearray(
        [0xaa, 0x4a, 0x4c, 0x0c, 0x00, 0x82, 0x03, 0x00, 0x01, 0x33, 0x33, 0x44, 0x44, 0x02, 0x04, 0x01, 0x01]),
    'start_experiment': bytearray([0xaa, 0x4a, 0x4c, 0x05, 0x00, 0x84, 0x03, 0x00, 0x01, 0x47]),
    'end_experiment': bytearray([0xaa, 0x4a, 0x4c, 0x05, 0x00, 0x84, 0x03, 0x00, 0x01, 0x4f]),
    'beep': bytearray([0xaa, 0x4a, 0x4c, 0x09, 0x00, 0x84, 0x03, 0x00, 0x01, 0x41, 0x34, 0x05, 0x00, 0x00]),
    'beep_on_off': bytearray([0xaa, 0x4a, 0x4c, 0x06, 0x00, 0x84, 0x03, 0x00, 0x01, 0x42, 0x88]),
    'light_off_off': bytearray([0xaa, 0x4a, 0x4c, 0x06, 0x00, 0x84, 0x03, 0x00, 0x01, 0x4c, 0x88]),
    'electricity_on_off': bytearray([0xaa, 0x4a, 0x4c, 0x06, 0x00, 0x84, 0x03, 0x00, 0x01, 0x45, 0x88]),
    'gravity_data': bytearray([0xaa]),
    'flash_on': bytearray([0xaa, 0x4a, 0x4c, 0x06, 0x00, 0x84, 0x03, 0x00, 0x01, 0x45, 0x11]),
}


class FrightenDevice:
    def __init__(self, gui):
        self.gui = gui
        self.window = gui.window
        self.ser = gui.ser
        self.index = 0
        self.x = []
        self.y = []
        self.first_write = True

        self.fig = Figure(figsize=(self.window.winfo_screenwidth(), 3))
        self.chart = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack()

        self.keep_ask = True

        self.experiment_started = False

    def init_filename(self):
        self.file_name = strftime('%Y-%m-%d %H%M%S.csv', gmtime())

    def start(self):
        # thread = threading.Thread(target=self.display_data_from_port, args=[])
        # thread.daemon = True
        # thread.start()

        thread = threading.Thread(target=self.ask_gravity_data, args=[])
        thread.daemon = True
        thread.start()
        self.gui.change_status('开始询问重力数据……')

    def start_experiment(self):
        self.init_filename()
        self.experiment_started = True
        self.toggle_asking(False)
        for i, value in enumerate(self.gui.config['commands']):
            self.set_command(value)

    def stop_experiment(self):
        self.experiment_started = False

    def toggle_asking(self, on_off=None):
        if on_off != None:
            self.keep_ask = on_off
        else:
            if self.keep_ask:
                self.keep_ask = False
            else:
                self.keep_ask = True

    def handle_gravity_data(self, data):
        gravity_data = PPI.parse_gravity_data(data)
        self.gui.change_status('{}：{}g'.format(hex_decode(data), gravity_data))
        self.plot_gravity_data(gravity_data)
        if self.experiment_started:
            self.append_data_to_file(gravity_data)

    def ask_gravity_data(self):
        while self.ser.isOpen:
            if self.keep_ask:
                self.issue_command(bytearray([0xAA, 0x4A, 0x4C, 0x04, 0x00, 0x86, 0x0F, 0x00, 0x01]),
                                   self.handle_gravity_data)

    def issue_command(self, command, expected_response):
        if self.ser.isOpen:
            self.gui.change_status('发送命令：{}'.format(hex_decode(command)))
            self.last_command = command
            self.ser.write(command)
            try:
                self.get_response(expected_response)
            except TimeoutError:
                self.gui.change_status('超时未获得回复')
        else:
            self.gui.change_status('不能发送命令，COM 端口没有打开！')

    def plot_gravity_data(self, data):
        points_per_screen = 30

        try:
            self.index += 1
            # self.x.append(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
            self.x.append(self.index)
            self.y.append(data)

            self.chart.cla()
            self.chart.plot(self.x[-points_per_screen:], self.y[-points_per_screen:], 'bo--')
            # self.chart.set_xticklabels(self.x[-points_per_screen:], rotation=17)
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

    def get_response(self, expected_response=None, timeout=1):
        waited = 0

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
                if waited >= timeout:
                    raise TimeoutError

                sleep(0.1)
                waited += 0.1

    def set_command(self, command):
        threading.Timer(command['at'], lambda: self.execute_command(command)).start()

    def execute_command(self, command):
        print('executing command: {}..., at {}'.format(command['command'], gmtime()))
        if command['command'] == 'login':
            self.issue_command(commands['login'], command_responses['login'])
        if command['command'] == 'end experiment':
            self.issue_command(commands['end_experiment'], command_responses['end_experiment'])
            self.stop_experiment()
            messagebox.showinfo('实验结束！', '实验结束了！')
            self.toggle_asking(True)
