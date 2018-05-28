import tkinter as tk

import yaml


def is_stimulate(command):
    if 'stimulate' in command:
        if command['stimulate']:
            return 1
        else:
            return 0
    else:
        return 0


def is_module_checked(command, module_index):
    if 'module' in command and \
                    type(command['module']) is dict and \
                    module_index in command['module'] and \
                    command['module'][module_index] is True:
        return 1
    else:
        return 0


class ConfigureDialog:
    def __init__(self, parent):
        self.modal_window = tk.Toplevel(parent)
        # self.label = tk.Label(self.modal_window, text='实验配置')
        # self.label.pack()
        self.read_config()
        self.modal_window.grab_set()

    def save(self):
        self.modal_window.destroy()

    def save_config(self, config_file_path='./config.yaml'):
        with open(config_file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(self.config, outfile, default_flow_style=False, allow_unicode=True)

    def read_config(self, config_file_path='./config.yaml'):
        with open(config_file_path, 'r') as stream:
            self.config = yaml.load(stream)

        self.update_ui()

    def update_ui(self):
        row = 0
        for key, value in self.config.items():
            print(key, value, type(value))
            if type(value) is not list:
                label = tk.Label(self.modal_window, text=key)
                label.grid(row=row, column=0, sticky=tk.W)

                the_value = tk.StringVar()
                the_value.set(value)
                input_box = tk.Entry(self.modal_window, textvariable=the_value)
                input_box.grid(row=row, column=1, sticky=tk.W)
                row += 1
            else:
                label = tk.Label(self.modal_window, text=key)
                label.grid(row=row, column=0, sticky=tk.W)
                row += 1

                for o in self.config[key]:
                    self.make_command_name_label(o, row)
                    row += 1

                    self.make_is_stimulate_checkbox(o, row)
                    self.make_at_field(o, row)
                    self.make_modules_checkboxes(o, row)

                    row += 1

    def make_command_name_label(self, o, row):
        label = tk.Label(self.modal_window, text=o['command'])
        label.grid(row=row, column=0, sticky=tk.W)

    def make_at_field(self, o, row):
        label = tk.Label(self.modal_window, text='触发时间')
        label.grid(row=row, column=2, sticky=tk.W)
        at_text = tk.StringVar(value=o['at'])
        text_box = tk.Entry(self.modal_window, width=20, textvariable=at_text)
        text_box.grid(row=row, column=3, sticky=tk.W)

    def make_is_stimulate_checkbox(self, command, row):
        command['is_stimulate'] = tk.IntVar(value=is_stimulate(command))
        chk = tk.Checkbutton(self.modal_window, text='刺激', variable=command['is_stimulate'], onvalue=1,
                             offvalue=0)
        chk.grid(row=row, column=1, sticky=tk.W)

    def make_modules_checkboxes(self, command, row):
        self.make_module_checkbox(command, 1, row, 5)
        self.make_module_checkbox(command, 2, row, 6)
        self.make_module_checkbox(command, 3, row, 7)
        self.make_module_checkbox(command, 4, row, 8)

    def make_module_checkbox(self, command, module_index, row, col):
        command['module_' + str(module_index) + '_check'] = tk.IntVar(value=is_module_checked(command, module_index))
        chk = tk.Checkbutton(self.modal_window, text='模块 ' + str(module_index),
                             variable=command['module_' + str(module_index) + '_check'],
                             onvalue=1, offvalue=0)
        chk.grid(row=row, column=col, sticky=tk.W)
