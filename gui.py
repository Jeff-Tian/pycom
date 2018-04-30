# encoding=utf-8
import threading
from tkinter import filedialog

import matplotlib.pyplot as plt
from time import gmtime, sleep
from time import strftime

import serial

from DataGenerator import *
from DataVisualizer import DataVisualizer
from FrightenDevice import FrightenDevice, command_responses, commands
import sys
import yaml

from helper import hex_decode

__author__ = 'freedom'
__all__ = ['hex_decode']

from tkinter import *
from serial import *
from tkinter import ttk
import serial.tools.list_ports
from tkinter import messagebox


def bind_event_data(widget, sequence, func, add=None):
    def _substitute(*args):
        e = lambda: None  # simplest object with __dict__
        e.data = args[0]  # eval(args[0])
        e.widget = widget
        return (e,)

    funcid = widget._register(func, _substitute, needcleanup=1)
    cmd = '{0}if {{"[{1} %d]" == "break"}} break\n'.format('+' if add else '', funcid)
    widget.tk.call('bind', widget._w, sequence, cmd)


class GUI(Frame):
    def __init__(self, window, debug_mode=False):

        self.debug_mode = debug_mode
        print('debug mode = ', self.debug_mode)
        window.title('动物惊吓实验')

        self.make_status_bar(window)
        self.make_menu_bar(window)

        self.window = window
        frame = Frame(window)
        frame.pack()

        # 串口设置相关变量
        self.port = "0"
        self.baudrate = 9600
        # 串口号提示
        self.lab1 = Label(frame, text='序列号')
        self.lab1.grid(row=0, column=0, sticky=W)

        self.init_serial()
        self.make_com_list(frame)
        # 输出框提示
        self.lab3 = Label(frame, text='收到的信息')
        self.lab3.grid(row=0, column=1, sticky=W)
        # 输出框
        self.show = Text(frame, width=40, height=5, wrap=WORD)
        self.show.grid(row=1, column=1, rowspan=4, sticky=W)
        # 输入框提示
        self.lab4 = Label(frame, text='要发送的信息')
        self.lab4.grid(row=5, column=1, sticky=W)
        # 输入框
        self.input = Entry(frame, width=40)
        self.input.grid(row=6, column=1, rowspan=4, sticky=W)
        # 输入按钮
        self.button1 = Button(frame, text="发送", command=self.submit)
        self.button1.grid(row=11, column=1, sticky=E)
        # 串口开启按钮
        self.button2 = Button(frame, text='打开串口', command=self.open_serial)
        self.button2.grid(row=7, column=0, sticky=W)
        # 串口关闭按钮
        self.button3 = Button(frame, text='关闭串口', command=self.close_serial)
        self.button3.grid(row=10, column=0, sticky=W)

        window.protocol('WM_DELETE_WINDOW', self.close_window)

        bind_event_data(window, '<<data_received>>', self.data_received)

        self.read_config()

    def make_status_bar(self, window):
        status = Label(window, text="准备就绪", bd=1, relief=SUNKEN, anchor=W)
        status.pack(side=BOTTOM, fill=X)
        self.status_bar = status

    def change_status(self, text=None):
        self.status_bar.config(text=text)
        self.status_bar.update_idletasks()
        self.status_bar.update_idletasks()

    def make_menu_bar(self, window):
        menu_bar = Menu(window)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='打开数据文件', command=self.open_file)
        file_menu.add_command(label='加载配置', command=self.read_config)
        file_menu.add_command(label='保存配置', command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.close_window)
        menu_bar.add_cascade(label='文件', menu=file_menu)

        command_menu = Menu(menu_bar, tearoff=0)
        command_menu.add_command(label='登录 AA 4A 4C 0C 00 81 02 00 01 11 11 22 22 02 04 01 01',
                                 command=lambda: self.issue_command(commands['login'], command_responses['login']))
        command_menu.add_command(label='开始试验 AA 4A 4C 05 00 84 02 00 01 47', command=lambda: self.issue_command(
            commands['start_experiment'], command_responses['start_experiment']))
        command_menu.add_command(label='结束试验 AA 4A 4C 05 00 84 02 00 01 4F', command=lambda: self.issue_command(
            commands['end_experiment'], command_responses['end_experiment']))
        command_menu.add_command(label='蜂鸣器频率设置 AA 4A 4C 09 00 84 02 00 01 41 34 05 00 00',
                                 command=lambda: self.issue_command(commands['beep'], command_responses['beep']))
        command_menu.add_command(label='蜂鸣器开关 AA 4A 4C 06 00 84 02 00 01 42 88', command=lambda: self.issue_command(
            commands['beep_on_off'],
            command_responses['beep_on_off']))
        command_menu.add_command(label='灯光开关 AA 4A 4C 06 00 84 02 00 01 4C 88', command=lambda: self.issue_command(
            commands['light_on_off'],
            command_responses['light_off_off']))
        command_menu.add_command(label='加电开关 AA 4A 4C 06 00 84 02 00 01 45 88', command=lambda: self.issue_command(
            commands['electricity_on_off'],
            command_responses['electricity_on_off']))
        command_menu.add_command(label='重力数据返回 AA 4A 4C 04 00 86 0F 00 01', command=lambda: self.issue_command(
            commands['gravity_data'], command_responses['gravity_data']))
        command_menu.add_command(label='亮灯 AA 4A 4C 06 00 84 02 00 01 45 11', command=lambda: self.issue_command(
            commands['flash_on'],
            command_responses['flash_on']))

        menu_bar.add_cascade(label='命令', menu=command_menu)
        menu_bar.add_command(label='测试数据', command=self.generate_data)
        menu_bar.add_command(label='开始实验', command=self.start_experiment)

        window.config(menu=menu_bar)

    def start_experiment(self):
        self.frighten_device.start_experiment()

    def open_file(self):
        file_path = filedialog.askopenfilename(initialdir='.', title="选择文件", filetypes=[('逗号分隔文件', '*.*')])
        self.frighten_device.plot_csv(file_path)

    def read_config(self):
        with open('./config.yaml', 'r') as stream:
            self.config = yaml.load(stream)

        return self.config

    def save_config(self):
        with io.open('./config.yaml', 'w', encoding='utf8') as outfile:
            yaml.dump(self.config, outfile, default_flow_style=False, allow_unicode=True)

    def issue_command(self, command, expected_response):
        self.command_thread = threading.Thread(target=self.issue_command_in_another_thread,
                                               args=[command, expected_response])
        self.command_thread.daemon = True
        self.command_thread.start()

    def issue_command_in_another_thread(self, command, expected_response):
        if self.ser.is_open:
            self.ser.write(command)
            self.get_response(expected_response)
        else:
            messagebox.showinfo('不能发送命令', 'COM 端口没有打开！')

    def get_response(self, expected_response):
        while True:
            n = self.ser.inWaiting()
            if n > 0:
                data = self.ser.read(n)
                if data == expected_response:
                    messagebox.showinfo('成功', '命令执行成功。')
                else:
                    messagebox.showinfo('失败',
                                        '{}{}{}{}'.format('命令返回：', hex_decode(data), ' 期待：',
                                                          hex_decode(expected_response)))

                self.window.event_generate('<<data_received>>', when='tail', data=hex_decode(data))
                print('data = ', hex_decode(data))
                break
            else:
                sleep(0.1)

    def data_received(self, event):
        print(event.data)
        self.show.delete(0.0, END)
        self.show.insert(0.0, event.data)

    def generate_data(self):
        thread_data = threading.Thread(target=DataGenerator.randomize, args=[self, self.ser])
        thread_data.daemon = True
        thread_data.start()

    def init_serial(self):
        # 串口初始化配置
        self.ser = Serial(baudrate=115200, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE)
        self.frighten_device = FrightenDevice(self)
        self.make_frighten_controls()

    def make_com_list(self, frame):
        # 串口号选择下拉菜单
        self.selected_port = StringVar()
        self.ports_list = ttk.Combobox(frame, textvariable=self.selected_port, state='readonly')
        self.ports_list['value'] = self.get_available_com_ports()
        if len(self.ports_list['value']) > 0:
            self.ports_list.current(0)
            self.ports_list.bind('<<ComboboxSelected>>', self.select_port)
            self.ports_list.grid(row=1, column=0, sticky=W)
            self.select_port(None)

            if len(self.ports_list['value']) == 1:
                self.open_serial()
        else:
            if not self.debug_mode:
                messagebox.showinfo("程序停止", "没有可用的 COM 端口！")
                exit(1)

    def get_available_com_ports(self):
        ports = []
        for port in list(serial.tools.list_ports.comports()):
            ports.append(port[0])

        return ports

    def select_port(self, event):
        self.port = self.selected_port.get()

    def submit(self):
        context1 = self.input.get()
        print('about to write ', context1.encode('utf-8'))
        self.ser.write(bytearray(context1.encode('utf-8')))

    def open_serial(self):
        self.ser.setPort(self.port)
        self.ser.open()
        if self.ser.isOpen():
            self.change_status('串口已被打开！')
            self.frighten_device.start()

    def close_serial(self):
        self.ser.close()
        if not self.ser.isOpen():
            self.change_status('串口已被关闭！')

    def close_window(self):
        print('closing window')
        # self.ser.close()
        # self.window.destroy()
        self.window.quit()

    def read_from_port(self):
        while self.ser.isOpen():
            n = self.ser.inWaiting()
            if n > 0:
                response = self.ser.readline().decode('utf-8')
                print('response = ', strftime('%Y-%m-%d %H:%M:%S', gmtime()), response)
                self.append_data_to_file(response)

    def make_frighten_controls(self):
        chk = ttk.Checkbutton(self.window, text='持续询问重力数据', command=self.frighten_device.toggle_asking)
        # chk.grid(column=1, row=10, sticky=W)
        chk.pack(pady=0, side=LEFT)
        chk.state(['!alternate'])

        if self.frighten_device.keep_ask:
            chk.state(['selected'])
        else:
            chk.state(['!selected'])


def debug_mode(argv):
    try:
        print('debug mode = ', argv.index('--debug'))
        return True
    except ValueError as ex:
        print(ex)
        return False


if __name__ == '__main__':
    root = Tk()
    root.state('zoomed')
    app = GUI(root, debug_mode(sys.argv))
    root.mainloop()
