# encoding=utf-8
import serial

__author__ = 'freedom'

from tkinter import *
from serial import *
from tkinter import ttk
import serial.tools.list_ports


class GUI(Frame):
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        # 串口设置相关变量
        self.port = "0"
        self.baudrate = 9600
        # 串口号提示
        self.lab1 = Label(frame, text='Serial Number')
        self.lab1.grid(row=0, column=0, sticky=W)

        self.init_serial()
        self.make_com_list(frame)
        # 波特率选择提示
        self.lab2 = Label(frame, text='Baudrate Set')
        self.lab2.grid(row=2, column=0, sticky=W)
        # 波特率选择下拉菜单
        self.boxValueBaudrate = IntVar()
        self.BaudrateChoice = ttk.Combobox(frame, textvariable=self.boxValueBaudrate, state='readonly')
        self.BaudrateChoice['value'] = (9600, 115200)
        self.BaudrateChoice.current(0)
        self.BaudrateChoice.bind('<<ComboboxSelected>>', self.ChoiceBaudrate)
        self.BaudrateChoice.grid(row=3, column=0, sticky=W)
        # 输出框提示
        self.lab3 = Label(frame, text='Message Show')
        self.lab3.grid(row=0, column=1, sticky=W)
        # 输出框
        self.show = Text(frame, width=40, height=5, wrap=WORD)
        self.show.grid(row=1, column=1, rowspan=4, sticky=W)
        # 输入框提示
        self.lab4 = Label(frame, text='Input here,please!')
        self.lab4.grid(row=5, column=1, sticky=W)
        # 输入框
        self.input = Entry(frame, width=40)
        self.input.grid(row=6, column=1, rowspan=4, sticky=W)
        # 输入按钮
        self.button1 = Button(frame, text="Input", command=self.Submit)
        self.button1.grid(row=11, column=1, sticky=E)
        # 串口开启按钮
        self.button2 = Button(frame, text='Open Serial', command=self.open)
        self.button2.grid(row=7, column=0, sticky=W)
        # 串口关闭按钮
        self.button3 = Button(frame, text='Close Serial', command=self.close)
        self.button3.grid(row=10, column=0, sticky=W)
        # 串口信息提示框
        self.showSerial = Text(frame, width=20, height=2, wrap=WORD)
        self.showSerial.grid(row=12, column=0, sticky=W)
        self.init_serial()
        # self.ser.setBaudrate(self.baudrate)
        # self.ser.open()
        # print self.ser.isOpen()
        # print self.ser

    def init_serial(self):
        # 串口初始化配置
        self.ser = Serial()

    def make_com_list(self, frame):
        # 串口号选择下拉菜单
        self.selected_port = StringVar()
        self.ports_list = ttk.Combobox(frame, textvariable=self.selected_port, state='readonly')
        self.ports_list['value'] = self.get_available_com_ports()
        self.ports_list.current(0)
        self.ports_list.bind('<<ComboboxSelected>>', self.select_port)
        self.ports_list.grid(row=1, column=0, sticky=W)

        self.select_port(None)

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

    def Submit(self):
        context1 = self.input.get()
        print('about to write ', context1.encode('latin-1'))
        n = self.ser.write(context1.encode())
        output = self.ser.read(n)
        print(output)
        self.show.delete(0.0, END)
        self.show.insert(0.0, output)

    def open(self):
        print('opening...')
        print('port = ', self.port)
        self.ser.setPort(self.port)
        self.ser.open()
        if self.ser.isOpen():
            self.showSerial.delete(0.0, END)
            self.showSerial.insert(0.0, "Serial has been opend!")

    def close(self):
        self.ser.close()
        if not self.ser.isOpen():
            self.showSerial.delete(0.0, END)
            self.showSerial.insert(0.0, "Serial has been closed!")


root = Tk()
root.title("惊吓设置")
# root.geometry("3000x4000")
app = GUI(root)
root.mainloop()
