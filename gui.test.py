import unittest

from gui import hex_decode, GUI
from tkinter import *


class TestGui(unittest.TestCase):
    def test_hex_decode(self):
        self.assertEqual(['0xaa', '0xab'], hex_decode([0xaa, 0xab]))

    def test_config(self):
        gui = GUI(Tk(), False)
        config = gui.read_config()
        self.assertEqual(True, len((config['commands'])) > 0)


if __name__ == '__main__':
    unittest.main()
