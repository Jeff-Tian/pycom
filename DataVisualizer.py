import threading

from time import gmtime
from time import strftime

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import matplotlib.pyplot as plt

__all__ = ['DataVisualizer']


class DataVisualizer:
    def __init__(self, window, ser):
        self.file_name = strftime('%Y-%m-%d %H%M%S.csv', gmtime())
        self.window = window
        self.ser = ser
        self.index = 0
        self.x = []
        self.y = []

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
            n = self.ser.inWaiting()
            if n > 0:
                data = self.ser.readline().decode('utf-8')
                self.window.event_generate('<<data_received>>', when='tail', data=data)
                self.append_data_to_file(data)
                self.plot(data)

    def plot(self, data):
        self.index += 1
        self.x.append(self.index)
        self.y.append(data)

        self.chart.scatter(self.x, self.y, color='blue')
        self.canvas.draw()

    def append_data_to_file(self, data=None):
        with open(self.file_name, 'a') as data_file:
            data_file.writelines(['{}, {}'.format(strftime('%Y-%m-%d %H:%M:%S', gmtime()), data)])

    def write_data_to_file(self):
        with open(self.file_name, 'w') as data_file:
            data_file.writelines(['{}, {}'.format('timestamp', 'data'), '\n'])
