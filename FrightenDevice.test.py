import unittest

from tkinter import *

from FrightenDevice import command_responses


class TestFrightenDevice(unittest.TestCase):
    def test_commands(self):
        self.assertEqual(bytearray(
            [0xaa, 0x4a, 0x4c, 0x0c, 0x00, 0x82, 0x03, 0x00, 0x01, 0x33, 0x33, 0x44, 0x44, 0x02, 0x04, 0x01, 0x01]),
            command_responses['login'])


if __name__ == '__main__':
    unittest.main()
