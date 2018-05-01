import unittest

from tkinter import *

import pandas

from FrightenDevice import command_responses, FrightenDevice


class TestFrightenDevice(unittest.TestCase):
    def test_commands(self):
        self.assertEqual(bytearray(
            [0xaa, 0x4a, 0x4c, 0x0c, 0x00, 0x82, 0x03, 0x00, 0x01, 0x33, 0x33, 0x44, 0x44, 0x02, 0x04, 0x01, 0x01]),
            command_responses['login'])

    def test_report(self):
        frighten_device = FrightenDevice(None)
        frighten_device.current_pd = pandas.read_csv('test.csv', '\, *', engine='python')
        (first_start_time, p, pp, ppi, filtered) = frighten_device.report(1000, 3000)
        self.assertEqual('2018-04-30 13:48:26.800702', first_start_time)
        print(filtered)
        self.assertEqual(False, filtered.empty)
        self.assertEqual(2.2187225685142938e-43, p)
        self.assertEqual(2.1613967222464604e-43, pp)
        self.assertEqual(0.025837320574162694, ppi)


if __name__ == '__main__':
    unittest.main()
