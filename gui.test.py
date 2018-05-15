import unittest

from gui import GUI
from tkinter import *


class TestGui(unittest.TestCase):
    def test_config(self):
        gui = GUI(Tk(), False)
        config = gui.read_config()
        self.assertEqual(True, len((config['commands'])) > 0)
        self.assertEqual({1: True, 2: True, 3: True, 4: True}, config['commands'][0]['module'])
        self.assertEqual(None, config['commands'][1]['module'])
        self.assertEqual({1: False, 2: False, 3: False, 4: False}, config['commands'][3]['module'])
        self.assertEqual(0.01, config['pool_interval'])


if __name__ == '__main__':
    unittest.main()
