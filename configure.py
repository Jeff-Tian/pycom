import tkinter as tk

import yaml


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
                    label = tk.Label(self.modal_window, text=o['command'])
                    label.grid(row=row, column=0, sticky=tk.W)
                    row += 1
