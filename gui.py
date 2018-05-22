# encoding=utf-8
from tkinter import filedialog

from time import gmtime
from time import strftime

import serial

from FrightenDevice import FrightenDevice, command_responses, commands, printx
import yaml
import os
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
        window.title('动物惊吓实验')

        self.make_status_bar(window)
        self.make_menu_bar(window)

        self.window = window
        frame = Frame(window)
        frame.pack()

        self.frame = frame

        # 串口设置相关变量
        self.port = "0"
        # 串口号提示
        self.lab1 = Label(frame, text='序列号')
        self.lab1.grid(row=0, column=0, sticky=W)

        self.init_serial()
        self.make_com_list(frame)
        self.open_serial_button = Button(frame, text='打开串口', command=self.open_serial)
        self.open_serial_button.grid(row=0, column=3, sticky=W)
        # 串口关闭按钮
        self.close_serial_button = Button(frame, text='关闭串口', command=self.close_serial)
        self.close_serial_button.grid(row=0, column=4, sticky=W)

        window.protocol('WM_DELETE_WINDOW', self.close_window)

        # bind_event_data(window, '<<data_received>>', self.data_received)

        self.stimulate_lines = None
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
        file_menu.add_command(label='打开数据文件', command=self.open_data_file)
        file_menu.add_command(label='加载配置', command=self.read_config)
        file_menu.add_command(label='保存配置', command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.close_window)
        menu_bar.add_cascade(label='文件', menu=file_menu)

        command_menu = Menu(menu_bar, tearoff=0)
        command_menu.add_command(label='登录 ' + ' '.join(hex_decode(commands['login'])),
                                 command=lambda: self.issue_command(commands['login'], command_responses['login']))
        command_menu.add_command(label='开始试验 ' + ' '.join(hex_decode(commands['start_experiment'])),
                                 command=lambda: self.issue_command(
                                     commands['start_experiment'], command_responses['start_experiment']))
        command_menu.add_command(label='结束试验 ' + ' '.join(hex_decode(commands['end_experiment'])),
                                 command=lambda: self.issue_command(
                                     commands['end_experiment'], command_responses['end_experiment']))
        command_menu.add_command(label='蜂鸣器频率设置 ' + ' '.join(hex_decode(commands['beep'])),
                                 command=lambda: self.issue_command(commands['beep'], command_responses['beep']))
        command_menu.add_command(label='蜂鸣器开关 ' + ' '.join(hex_decode(commands['beep_on_off'])),
                                 command=lambda: self.issue_command(
                                     commands['beep_on_off'],
                                     command_responses['beep_on_off']))
        command_menu.add_command(label='灯光开关 ' + ' '.join(hex_decode(commands['light_on_off'])),
                                 command=lambda: self.issue_command(
                                     commands['light_on_off'],
                                     command_responses['light_on_off']))
        command_menu.add_command(label='加电开关 ' + ' '.join(hex_decode(commands['electricity_on_off'])),
                                 command=lambda: self.issue_command(
                                     commands['electricity_on_off'],
                                     command_responses['electricity_on_off']))
        command_menu.add_command(label='重力数据返回 ' + ' '.join(hex_decode(commands['gravity_data'])),
                                 command=lambda: self.issue_command(
                                     commands['gravity_data'], self.frighten_device.handle_gravity_data))
        command_menu.add_command(label='亮灯 ' + ' '.join(hex_decode(commands['flash_on_'])),
                                 command=lambda: self.issue_command(
                                     commands['flash_on_'],
                                     command_responses['flash_on_']))

        menu_bar.add_cascade(label='命令', menu=command_menu)
        menu_bar.add_command(label='开始实验', command=self.start_experiment)
        menu_bar.add_command(label='结束实验', command=self.stop_experiment)

        window.config(menu=menu_bar)

    def start_experiment(self):
        if self.frighten_device.experiment_started:
            messagebox.showinfo('试验进行中', '请等待试验结束后再开始')
            return

        self.read_config()
        self.frighten_device.start_experiment()

    def stop_experiment(self):
        if not self.frighten_device.experiment_started:
            messagebox.showinfo('试验未开始', '试验还未开始')
            return

        self.frighten_device.stop_experiment()

    def open_data_file(self):
        if self.frighten_device.experiment_started:
            messagebox.showinfo('实验正在进行', '请先结束试验！')
            return

        self.frighten_device.toggle_asking(False)
        data_file_path = filedialog.askopenfilename(initialdir='.', title="选择文件", filetypes=[('逗号分隔文件', '*.csv')])

        if data_file_path != '':
            self.frighten_device.plot_csv(data_file_path)

            config_file_path = os.path.splitext(data_file_path)[0] + '.yaml'

            try:
                self.read_config(config_file_path)
            except:
                self.read_config()
        else:
            self.change_status('打开文件取消。')

    def read_config(self, config_file_path='./config.yaml'):
        if self.frighten_device.experiment_started:
            messagebox.showinfo('实验正在进行', '请先结束试验！')
            return
        with open(config_file_path, 'r') as stream:
            self.config = yaml.load(stream)

        self.update_ui()
        return self.config

    def update_ui(self):
        self.make_report()

    def save_config(self):
        if self.frighten_device.experiment_started:
            messagebox.showinfo('实验正在进行', '请先结束试验！')
            return
        with io.open('./config.yaml', 'w', encoding='utf8') as outfile:
            yaml.dump(self.config, outfile, default_flow_style=False, allow_unicode=True)

    def issue_command(self, command, expected_response):
        if self.frighten_device.experiment_started:
            messagebox.showinfo('实验正在进行', '请先结束试验！')
            return

        self.frighten_device.toggle_asking(False)
        self.frighten_device.read_in_residual_data()
        self.frighten_device.issue_command(command, expected_response)
        self.frighten_device.restore_asking()

    def data_received(self, event):
        pass

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
            self.ports_list.grid(row=0, column=1, sticky=W)
            self.select_port(None)

            if len(self.ports_list['value']) == 1:
                self.open_serial()

    def get_available_com_ports(self):
        ports = []
        for port in list(serial.tools.list_ports.comports()):
            ports.append(port[0])

        return ports

    def select_port(self, event):
        self.port = self.selected_port.get()

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
        # self.ser.close()
        # self.window.destroy()
        self.window.quit()

    def make_frighten_controls(self):
        chk = ttk.Checkbutton(self.window, text='持续询问重力数据', command=self.frighten_device.toggle_asking)
        # chk.grid(column=1, row=10, sticky=W)
        chk.pack(pady=0, side=LEFT)
        chk.state(['!alternate'])

        if self.frighten_device.keep_ask:
            chk.state(['selected'])
        else:
            chk.state(['!selected'])

    def make_report(self):
        if self.stimulate_lines is not None:
            for key, value in self.stimulate_lines.items():
                self.stimulate_lines[key]['stimulate_name'].destroy()
                self.stimulate_lines[key]['label_start_at'].destroy()
                self.stimulate_lines[key]['start_at_input'].destroy()
                self.stimulate_lines[key]['label_end_at'].destroy()
                self.stimulate_lines[key]['end_at_input'].destroy()
                self.stimulate_lines[key]['ppi_button'].destroy()
                self.stimulate_lines[key]['text_report'].destroy()

        self.stimulate_lines = {}
        stimulate_commands = [command for command in self.config['commands'] if
                              ('stimulate' in command) and (command['stimulate'] == True)]
        for i in range(0, len(stimulate_commands)):
            self.make_stimulate(stimulate_commands[i], i)

    def make_stimulate(self, command, index=0):
        frame = self.frame
        self.stimulate_lines[index] = {}

        self.stimulate_lines[index]['stimulate_name'] = Label(frame, text=command['command'])
        self.stimulate_lines[index]['stimulate_name'].grid(row=index + 1, column=0, sticky=W)
        self.stimulate_lines[index]['label_start_at'] = Label(frame, text='开始时间（毫秒）')
        self.stimulate_lines[index]['label_start_at'].grid(row=index + 1, column=1, sticky=W)

        start_at_text = StringVar()
        start_at = command['at'] * 1000
        start_at_text.set(start_at)
        self.stimulate_lines[index]['start_at_input'] = Entry(frame, width=20, textvariable=start_at_text)
        self.stimulate_lines[index]['start_at_input'].grid(row=index + 1, column=2, sticky=W)
        self.stimulate_lines[index]['label_end_at'] = Label(frame, text='结束时间（毫秒）')
        self.stimulate_lines[index]['label_end_at'].grid(row=index + 1, column=3, sticky=W)
        end_at_text = StringVar()
        end_at = start_at + 200
        end_at_text.set(end_at)
        self.stimulate_lines[index]['end_at_input'] = Entry(frame, width=20, textvariable=end_at_text)
        self.stimulate_lines[index]['end_at_input'].grid(row=index + 1, column=4, sticky=W)
        self.stimulate_lines[index]['ppi_button'] = Button(frame, text="计算 PPI", command=lambda:
        self.report(command,
                    self.stimulate_lines[
                        index][
                        'start_at_input'].get(),
                    self.stimulate_lines[
                        index][
                        'end_at_input'].get(),
                    self.stimulate_lines[index]['text_report']))
        self.stimulate_lines[index]['ppi_button'].grid(row=index + 1, column=5, sticky=E)
        self.stimulate_lines[index]['text_report'] = Entry(frame, width=20)
        self.stimulate_lines[index]['text_report'].grid(row=index + 1, column=6, sticky=E)

        self.report(command, start_at, end_at, self.stimulate_lines[index]['text_report'])

    def report(self, command, start_at, end_at, text_report):
        (start_at, p, pp, ppi, data) = self.frighten_device.report(int(start_at), int(end_at))
        text_report.delete(0, END)
        text_report.insert(0, '{0:.4f}%'.format(ppi * 100))


def debug_mode(argv):
    try:
        print('debug mode = ', argv.index('--debug'))
        return True
    except ValueError as ex:
        return False


if __name__ == '__main__':
    root = Tk()
    root.state('zoomed')
    app = GUI(root, debug_mode(sys.argv))
    root.mainloop()
