import tkinter as tk


class ConfigureDialog:
    def __init__(self, parent):
        self.modal_window = tk.Toplevel(parent)
        self.label = tk.Label(self.modal_window, text='实验配置')
        self.label.pack()
        self.modal_window.grab_set()

    def save(self):
        self.modal_window.destroy()
