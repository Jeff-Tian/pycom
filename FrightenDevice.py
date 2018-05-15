import struct
import threading

from time import gmtime, sleep
from time import strftime
from tkinter import messagebox

import io

import yaml
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
import numpy as np

import pandas as pd

from  PPI import *
from helper import hex_decode

__all__ = ['FrightenDevice', 'commands', 'command_responses', 'printx']

date_time_format = '%Y-%m-%d %H:%M:%S.%f'


def printx(arg1, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None):
    # print(arg1, arg2, arg3, arg4, arg5, arg6)
    pass


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
    'flash_on_': bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x4C, 0x11]),
}

command_responses = {
    'login': bytearray(
        [0xaa, 0x4a, 0x4c, 0x0c, 0x00, 0x82, 0x03, 0x00, 0x01, 0x33, 0x33, 0x44, 0x44, 0x02, 0x04, 0x01, 0x01]),
    'start_experiment': bytearray([0xaa, 0x4a, 0x4c, 0x05, 0x00, 0x84, 0x03, 0x00, 0x01, 0x47]),
    'end_experiment': bytearray([0xaa, 0x4a, 0x4c, 0x05, 0x00, 0x84, 0x03, 0x00, 0x01, 0x4f]),
    'beep': bytearray([0xaa, 0x4a, 0x4c, 0x09, 0x00, 0x84, 0x03, 0x00, 0x01, 0x41, 0x34, 0x05, 0x00, 0x00]),

    'beep_on_off': bytearray([0xaa, 0x4a, 0x4c, 0x06, 0x00, 0x84, 0x03, 0x00, 0x01, 0x42, 0x88]),
    'light_on_off': bytearray([0xaa, 0x4a, 0x4c, 0x06, 0x00, 0x84, 0x03, 0x00, 0x01, 0x4c, 0x88]),
    'electricity_on_off': bytearray([0xaa, 0x4a, 0x4c, 0x06, 0x00, 0x84, 0x03, 0x00, 0x01, 0x45, 0x88]),
    'gravity_data': bytearray([0xaa]),
    'flash_on': bytearray([0xaa, 0x4a, 0x4c, 0x06, 0x00, 0x84, 0x03, 0x00, 0x01, 0x45, 0x11]),
    'flash_on_': bytearray([0xaa, 0x4a, 0x4c, 0x06, 0x00, 0x84, 0x03, 0x00, 0x01, 0x4C, 0x11]),
}


def mask(df, f):
    return df[f(df)]


class FrightenDevice:
    def __init__(self, gui):
        self.gui = gui
        if gui != None:
            self.window = gui.window
            self.ser = gui.ser
        self.index = 0
        self.x = []
        self.y = []
        self.first_write = True
        self.current_pd = None

        if gui is not None:
            self.fig = Figure(figsize=(self.window.winfo_screenwidth(), 6))
            self.chart = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
            self.canvas.get_tk_widget().pack()

        self.keep_ask = False

        self.experiment_started = False

    def init_filename(self):
        self.file_name = strftime('%Y-%m-%d %H%M%S.csv', gmtime())
        self.config_file_name = strftime('%Y-%m-%d %H%M%S.yaml', gmtime())

    def start(self):
        # thread = threading.Thread(target=self.display_data_from_port, args=[])
        # thread.daemon = True
        # thread.start()

        thread = threading.Thread(target=self.ask_gravity_data, args=[])
        thread.daemon = True
        thread.start()
        self.gui.change_status('开始询问重力数据……')

    def exit(self):
        self.experiment_started = False
        self.toggle_asking(False)

    def login(self):
        self.gui.change_status('登录中……')
        self.issue_command(commands['login'], command_responses['login'], 3)

    def start_experiment(self):
        try:
            self.login()
        except:
            self.exit()
            messagebox.showinfo('实验未能开始', '登录失败！')
            return

        messagebox.showinfo('实验开始！', '实验要开始了！')
        self.init_filename()
        self.experiment_started = True
        self.toggle_asking(True)

        try:
            self.issue_command(commands['start_experiment'], command_responses['start_experiment'], 3)
        except:
            self.exit()
            messagebox.showinfo('实验未能开始', '设备未能正确应答')
            return

        for i, value in enumerate(self.gui.config['commands']):
            self.set_command(value)

    def stop_experiment(self):
        self.exit()
        self.read_in_residual_data()
        self.issue_command(commands['end_experiment'], command_responses['end_experiment'])
        messagebox.showinfo('实验结束！', '实验结束了！')
        printx('实验结束！')

    def restore_asking(self):
        if self.last_asking_status is not None:
            self.keep_ask = self.last_asking_status

    def toggle_asking(self, on_off=None):
        self.last_asking_status = self.keep_ask
        if on_off is not None:
            self.keep_ask = on_off
        else:
            if self.keep_ask:
                self.keep_ask = False
            else:
                self.keep_ask = True

        printx('asking = ', self.keep_ask)

    def handle_gravity_data(self, data):
        gravity_data = PPI.parse_gravity_data(data)
        # self.gui.change_status('{}：{}g'.format(hex_decode(data), gravity_data))
        self.plot_gravity_data(gravity_data)
        if self.experiment_started:
            self.append_data_to_file(gravity_data)

    def ask_gravity_data(self):
        while self.ser.isOpen:
            if self.keep_ask:
                self.issue_command(commands['gravity_data'],
                                   self.handle_gravity_data)
                sleep(1)

    def issue_command(self, command, expected_response, retry_times=0):
        if self.ser.isOpen:
            self.gui.change_status('发送命令：{}'.format(hex_decode(command)))
            self.last_command = command
            try:
                try:
                    self.ser.write(command)

                    try:
                        self.get_response(expected_response)
                    except TimeoutError:
                        self.gui.change_status('超时未获得回复')
                        raise
                    except Exception as ex:
                        self.gui.change_status(ex)
                        raise
                except Exception as ex:
                    print(ex)
                    self.gui.change_status('串口通信写入失败！')
                    raise
            except:
                if retry_times > 0:
                    self.issue_command(command, expected_response, retry_times - 1)
                else:
                    self.gui.change_status('重试了几次，仍然失败了……'.format(retry_times))
                    raise
        else:
            self.gui.change_status('不能发送命令，COM 端口没有打开！')

    def plot_gravity_data(self, data):
        points_per_screen = 30

        try:
            self.index += 1 * 30
            self.x += [i + self.index for i in range(30)]
            self.y = self.y + data

            self.chart.cla()
            self.chart.plot(self.x[-points_per_screen:], self.y[-points_per_screen:], 'bo--')
            # self.chart.set_xticklabels(self.x[-points_per_screen:], rotation=17)
            self.chart.set_title(label=u'PP = {}'.format(np.average(self.y)))
            self.canvas.draw()
        except ValueError as ex:
            printx(ex)
            pass

    def compute_ppi(self):
        pass

    def plot_csv(self, csv_file):
        self.gui.change_status('正在读取文件……')
        data = pd.read_csv(csv_file, '\, *', engine='python')
        self.current_pd = data
        self.gui.change_status('读取文件完毕，正在画图……')
        # self.x = data.timestamp
        try:
            self.x = [i for i in range(len(data.data))]
            print('self.x = ', self.x)
            self.y = data.data

            self.chart.cla()
            self.chart.clear()

            self.chart.plot(self.x, self.y, 'bo--')
            # self.chart.set_xticklabels(self.x, rotation=17)
            self.chart.set_title(label=u'PP = {}'.format(np.average(self.y)))
            self.canvas.draw()
        except Exception as ex:
            print(ex)
            messagebox.showinfo('画图失败！', '可能是文件格式不对，或者没有数据。')
        self.gui.change_status('画图完毕.')
        self.compute_ppi()

    def append_data_to_file(self, data=None):
        if self.first_write:
            self.write_file()
            self.first_write = False

        with open(self.file_name, 'a') as data_file:
            if data is not None:
                need_to_write = []
                start = datetime.datetime.utcnow()
                stop = len(data)
                for i in range(stop):
                    start += datetime.timedelta(seconds=1 / stop)
                    need_to_write.append(
                        '{},{}'.format(start.strftime('%Y-%m-%d %H:%M:%S.%f'), data[i]))
                    need_to_write.append('\n')

                data_file.writelines(need_to_write)

    def write_file(self):
        with open(self.file_name, 'w') as data_file:
            data_file.writelines(['{},{}'.format('timestamp', 'data'), '\n'])
        with io.open(self.config_file_name, 'w', encoding='utf8') as config_file:
            yaml.dump(self.gui.config, config_file, default_flow_style=False, allow_unicode=True)

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

                sleep(self.gui.config['pool_interval'])
                waited += self.gui.config['pool_interval']

    def set_command(self, command):
        threading.Timer(command['at'], lambda: self.execute_command(command)).start()

    def execute_command(self, command):
        if not self.experiment_started:
            printx('skipping command: {}... at {}'.format(command['command'].encode('utf-8').decode('utf8'), gmtime()))
            return

        printx('executing command: {}..., at {}'.format(command['command'].encode('utf8').decode('utf8'), gmtime()))
        self.toggle_asking(False)
        self.read_in_residual_data()

        if command['command'] == 'light on':
            self.light_on()
        if command['command'] == 'light off':
            self.light_off()
        if command['command'] == 'electricity on':
            self.electricity_on()
        if command['command'] == 'electricity off':
            self.electricity_off()
        if command['command'] == 'noise setting':
            self.set_noise()
        if command['command'] == 'noise on':
            self.noise_on(command)
        if command['command'] == 'flash on':
            self.flash_on()
        if command['command'] == 'end experiment':
            self.stop_experiment()

        self.restore_asking()
        printx('asking again')

    def flash_on(self):
        self.issue_command(commands['flash_on'], command_responses['flash_on'])

    def noise_on(self, command):
        self.issue_command(self.get_beep_setting(command), self.get_beep_setting_response(command))
        self.issue_command(commands['beep_on_off'], command_responses['beep_on_off'])

    def set_noise(self):
        self.issue_command(commands['beep'], command_responses['beep'])

    def electricity_off(self):
        self.issue_command(commands['electricity_on_off'], command_responses['electricity_on_off'])

    def electricity_on(self):
        self.issue_command(commands['electricity_on_off'], command_responses['electricity_on_off'])

    def light_off(self):
        self.issue_command(commands['light_on_off'], command_responses['light_on_off'])

    def light_on(self):
        self.issue_command(commands['light_on_off'], command_responses['light_on_off'])

    def read_in_residual_data(self):
        n = self.ser.inWaiting()
        while n > 0:
            self.ser.read(n)
            sleep(self.gui.config['pool_interval'])
            n = self.ser.inWaiting()

    def report(self, start_time_in_ms, end_time_in_ms):
        if self.current_pd is not None:
            experiment_start_at = self.current_pd.timestamp[0]
            start_at = datetime.datetime.strptime(experiment_start_at, date_time_format)
            filter_start = start_at + datetime.timedelta(microseconds=start_time_in_ms * 1000)
            filter_end = start_at + datetime.timedelta(microseconds=end_time_in_ms * 1000)

            filter_start = datetime.datetime.strftime(filter_start, date_time_format)
            filter_end = datetime.datetime.strftime(filter_end, date_time_format)

            filtered_data = self.current_pd[
                (self.current_pd.timestamp >= filter_start) & (self.current_pd.timestamp < filter_end)]

            return (experiment_start_at,) + PPI.get_ppi(self.current_pd.data, filtered_data.data) + (filtered_data,)
        else:
            return 0, 0, 0, 0, 0

    def get_beep_setting(self, command):
        return bytearray(
            [0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, self.get_beep_module(int(command['module']))] +
            self.get_beep_frequency(int(command['frequency'])))

    def get_beep_frequency(self, freq=5):
        bytes = struct.pack('L', freq)

        return [bytes[0], bytes[1], bytes[2]]

    def get_beep_setting_response(self, command):
        return bytearray(
            [0xaa, 0x4a, 0x4c, 0x09, 0x00, 0x84, 0x03, 0x00, 0x01, 0x41, self.get_beep_module(int(command['module'])),
             0x05,
             0x00,
             0x00])

    def get_beep_module(self, module=1):
        if module == 1:
            return 0x31
        if module == 2:
            return 0x32
        if module == 3:
            return 0x33
        if module == 4:
            return 0x34

        return 0x34
