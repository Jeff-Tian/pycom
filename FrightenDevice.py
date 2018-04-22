import threading

from time import gmtime, sleep
from time import strftime

from matplotlib import dates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

import pandas as pd

__all__ = ['FrightenDevice']


class FrightenDevice:
    def __init__(self, window, ser):
        self.file_name = strftime('%Y-%m-%d %H%M%S.csv', gmtime())
        self.window = window
        self.ser = ser
        self.index = 0
        self.x = []
        self.y = []
        self.first_write = True

        self.fig = Figure(figsize=(window.winfo_screenwidth(), 6))
        self.chart = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack()

    def start(self):
        thread = threading.Thread(target=self.display_data_from_port, args=[])
        thread.daemon = True
        thread.start()

    def display_data_from_port(self):
        while self.ser.isOpen():
            n = self.ser.inWaiting()
            if n > 0:
                data = self.ser.read(n)
                data = [hex(c) for c in data]
                self.window.event_generate('<<data_received>>', when='tail', data=data)
                print(data)

    def plot(self, data):
        try:
            self.index += 1
            self.x.append(self.index)
            self.y.append(data)

            self.chart.scatter(self.x, self.y, color='blue')
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
