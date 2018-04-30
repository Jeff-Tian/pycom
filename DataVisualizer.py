import threading

from time import gmtime, sleep
from time import strftime

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import pandas as pd

__all__ = ['DataVisualizer']


class DataVisualizer:
    def __init__(self, window, ser):
        self.file_name = strftime('%Y-%m-%d %H%M%S.csv', gmtime())
        self.window = window
        self.ser = ser
        self.index = 0
        self.x = []
        self.y = []
        self.first_write = True

        self.fig = Figure(figsize=(6, 6))
        self.chart = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack()

    def start(self):
        thread = threading.Thread(target=self.display_data_from_port, args=[])
        thread.daemon = True
        thread.start()

    def display_data_from_port(self):
        while self.ser.isOpen():
            printx('reading...')
            data = self.ser.readline()
            data = data.decode('utf-8')[:-1]
            self.window.event_generate('<<data_received>>', when='tail', data=data)
            self.append_data_to_file(data)
            self.plot(data)

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
        self.x = [i for i in range(len(data.data))]
        self.y = data.data
        self.chart.scatter(self.x, self.y)
        self.canvas.draw()

    def append_data_to_file(self, data=None):
        if self.first_write:
            self.write_data_to_file()
            self.first_write = False

        with open(self.file_name, 'a') as data_file:
            data_file.writelines(['{},{}'.format(strftime('%Y-%m-%d %H:%M:%S', gmtime()), data), '\n'])

    def write_data_to_file(self):
        with open(self.file_name, 'w') as data_file:
            data_file.writelines(['{},{}'.format('timestamp', 'data'), '\n'])
