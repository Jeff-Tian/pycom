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
        self.assertEqual(3.363116314379577e-45, p)
        self.assertEqual(3.5032461608120439e-45, pp)
        self.assertEqual(-0.041666666666662064, ppi)

    def test_noise_setting_command(self):
        frighten_device = FrightenDevice(None)

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x31, 0x05, 0x00, 0x00]),
            frighten_device.get_beep_setting({
                'module': 1
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x32, 0x05, 0x00, 0x00]),
            frighten_device.get_beep_setting({
                'module': 2
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x33, 0x05, 0x00, 0x00]),
            frighten_device.get_beep_setting({
                'module': 3
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x34, 0x05, 0x00, 0x00]),
            frighten_device.get_beep_setting({
                'module': 4
            })
        )

        self.assertEqual(
            bytearray([0xaa, 0x4a, 0x4c, 0x09, 0x00, 0x84, 0x03, 0x00, 0x01, 0x41, 0x34, 0x05, 0x00, 0x00]),
            frighten_device.get_beep_setting_response({
                'module': 4
            })
        )


if __name__ == '__main__':
    unittest.main()
