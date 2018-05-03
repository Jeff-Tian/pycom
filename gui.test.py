import unittest

from gui import GUI
from tkinter import *


class TestGui(unittest.TestCase):
    def test_config(self):
        gui = GUI(Tk(), False)
        config = gui.read_config()
        self.assertEqual(True, len((config['commands'])) > 0)
        self.assertEqual(0.01, config['pool_interval'])


if __name__ == '__main__':
    unittest.main()
