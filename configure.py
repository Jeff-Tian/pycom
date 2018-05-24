import tkinter as tk

import yaml


class ConfigureDialog:
    def __init__(self, parent):
        self.modal_window = tk.Toplevel(parent)
        self.label = tk.Label(self.modal_window, text='实验配置')
        self.label.pack()
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
        pass
