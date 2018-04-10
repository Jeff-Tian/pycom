# encoding=utf-8
import threading
import matplotlib.pyplot as plt
from time import gmtime
from time import strftime

import serial

from DataGenerator import *
from DataVisualizer import DataVisualizer

__author__ = 'freedom'

from tkinter import *
from serial import *
from tkinter import ttk
import serial.tools.list_ports
from tkinter import messagebox


def bind_event_data(widget, sequence, func, add=None):
    def _substitute(*args):
        e = lambda: None  # simplest object with __dict__
        e.data = eval(args[0])
        e.widget = widget
        return (e,)

    funcid = widget._register(func, _substitute, needcleanup=1)
    cmd = '{0}if {{"[{1} %d]" == "break"}} break\n'.format('+' if add else '', funcid)
    widget.tk.call('bind', widget._w, sequence, cmd)


class GUI(Frame):
    def __init__(self, master):
        self.master = master
        master.title('动物惊吓实验')
        frame = Frame(master)
        frame.pack()
        # 串口设置相关变量
        self.port = "0"
        self.baudrate = 9600
        # 串口号提示
        self.lab1 = Label(frame, text='序列号')
        self.lab1.grid(row=0, column=0, sticky=W)
        self.status_box(frame)
        self.init_serial()
        self.make_com_list(frame)
        # 波特率选择提示
        self.lab2 = Label(frame, text='波特率')
        self.lab2.grid(row=2, column=0, sticky=W)
        self.make_baudrate_list(frame)
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

        master.protocol('WM_DELETE_WINDOW', self.close_window)

        self.data_button = Button(frame, text='模拟数据', command=self.generate_data)
        self.data_button.grid(row=14, column=1, sticky=W)

        # master.bind('<<data_received>>', self.data_received)
        bind_event_data(master, '<<data_received>>', self.data_received)

    def data_received(self, event):
        data = event.data

    def status_box(self, frame):
        # 串口信息提示框
        self.showSerial = Text(frame, width=20, height=2, wrap=WORD)
        self.showSerial.grid(row=12, column=0, sticky=W)

    def generate_data(self):
        thread_data = threading.Thread(target=DataGenerator.randomize, args=[self.ser])
        thread_data.daemon = True
        thread_data.start()

    def make_baudrate_list(self, frame):
        # 波特率选择下拉菜单
        self.boxValueBaudrate = IntVar()
        self.BaudrateChoice = ttk.Combobox(frame, textvariable=self.boxValueBaudrate, state='readonly')
        self.BaudrateChoice['value'] = (9600, 115200)
        self.BaudrateChoice.current(0)
        self.BaudrateChoice.bind('<<ComboboxSelected>>', self.ChoiceBaudrate)
        self.BaudrateChoice.grid(row=3, column=0, sticky=W)
        self.closing = False

    def init_serial(self):
        # 串口初始化配置
        self.ser = Serial()

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
            messagebox.showinfo("程序停止", "没有可用的 COM 端口！")
            exit(1)

    def get_available_com_ports(self):
        ports = []
        for port in list(serial.tools.list_ports.comports()):
            ports.append(port[0])

        return ports

    def select_port(self, event):
        self.port = self.selected_port.get()

    def ChoiceBaudrate(self, event):
        self.baudrate = self.boxValueBaudrate.get()
        self.ser.setBaudrate(self.baudrate)
        print(self.baudrate)

    def submit(self):
        context1 = self.input.get() + '\n'
        print('about to write ', context1.encode('utf-8'))
        self.ser.write(context1.encode('utf-8'))
        # self.show.delete(0.0, END)
        # self.show.insert(0.0, output)

    def open_serial(self):
        self.ser.setPort(self.port)
        self.ser.open()
        if self.ser.isOpen():
            self.index = 0
            self.showSerial.delete(0.0, END)
            self.showSerial.insert(0.0, "Serial has been opened!")
            self.data_visualizer = DataVisualizer(self.master, self.ser)
            self.data_visualizer.start()

    def close_serial(self):
        self.ser.close()
        if not self.ser.isOpen():
            self.showSerial.delete(0.0, END)
            self.showSerial.insert(0.0, "Serial has been closed!")

    def close_window(self):
        print('closing window')
        self.ser.close()
        self.master.destroy()

    def read_from_port(self):
        while self.ser.isOpen():
            n = self.ser.inWaiting()
            if n > 0:
                response = self.ser.readline().decode('utf-8')
                print('response = ', strftime('%Y-%m-%d %H:%M:%S', gmtime()), response)
                self.append_data_to_file(response)


root = Tk()
# root.geometry("3000x4000")
app = GUI(root)

root.mainloop()
