import unittest

from tkinter import *

import pandas

from FrightenDevice import command_responses, FrightenDevice


class TestFrightenDevice(unittest.TestCase):
    def test_toggle(self):
        fd = FrightenDevice(None)
        self.assertEqual(fd.keep_ask, True)

        fd.toggle_asking(False)
        self.assertEqual(True, fd.last_asking_status)
        fd.toggle_asking(False)
        self.assertEqual(True, fd.last_asking_status)

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

    def test_beep_set_module(self):
        frighten_device = FrightenDevice(None)

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x31, 0x05, 0x00, 0x00]),
            frighten_device.get_beep_setting({
                'module': 1,
                'frequency': 5
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x32, 0x05, 0x00, 0x00]),
            frighten_device.get_beep_setting({
                'module': 2,
                'frequency': 5
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x33, 0x05, 0x00, 0x00]),
            frighten_device.get_beep_setting({
                'module': 3,
                'frequency': 5
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x34, 0x05, 0x00, 0x00]),
            frighten_device.get_beep_setting({
                'module': 4,
                'frequency': 5
            })
        )

        self.assertEqual(
            bytearray([0xaa, 0x4a, 0x4c, 0x09, 0x00, 0x84, 0x03, 0x00, 0x01, 0x41, 0x34, 0x05, 0x00, 0x00]),
            frighten_device.get_beep_setting_response({
                'module': 4,
                'frequency': 5
            })
        )

    def test_beep_set_frequency(self):
        frighten_device = FrightenDevice(None)

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x31, 0xe8, 0x03, 0x00]),
            frighten_device.get_beep_setting({
                'module': 1,
                'frequency': 1000
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x31, 0xff, 0x00, 0x00]),
            frighten_device.get_beep_setting({
                'module': 1,
                'frequency': 255
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x09, 0x00, 0x84, 0x02, 0x00, 0x01, 0x41, 0x31, 0xff, 0x00, 0x00]),
            frighten_device.get_beep_setting({
                'module': 1,
                'frequency': 255
            })
        )

    def test_beep_on_off(self):
        frighten_device = FrightenDevice(None)

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x42, 0x77]),
            frighten_device.get_beep_on({
                'module': {
                    '1': True,
                    '2': True,
                    '3': True,
                    '4': False
                }
            })
        )

    def test_electricity_on_off(self):
        frighten_device = FrightenDevice(None)

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x45, 0x88]),
            frighten_device.get_electricity_on_off({
                'module': {
                    '4': True
                }
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x45, 0x44]),
            frighten_device.get_electricity_on_off({
                'module': {
                    '3': True
                }
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x45, 0xaa]),
            frighten_device.get_electricity_on_off({
                'module': {
                    '2': True,
                    '4': True
                }
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x45, 0xff]),
            frighten_device.get_electricity_on_off({
                'module': {
                    '1': True,
                    '2': True,
                    '3': True,
                    '4': True
                }
            })
        )

    def test_light_on_off(self):
        frighten_device = FrightenDevice(None)

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x4C, 0xff]),
            frighten_device.get_light_on_off({
                'module': {
                    '1': True,
                    '2': True,
                    '3': True,
                    '4': True
                }
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x4C, 0x00]),
            frighten_device.get_light_on_off({
                'module': {}
            })
        )

        self.assertEqual(
            bytearray([0xAA, 0x4A, 0x4C, 0x06, 0x00, 0x84, 0x02, 0x00, 0x01, 0x4C, 0x00]),
            frighten_device.get_light_on_off({
                'module': None
            })
        )


if __name__ == '__main__':
    unittest.main()
