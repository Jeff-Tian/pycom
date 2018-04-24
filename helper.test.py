import unittest

from helper import hex_decode


class TestHelper(unittest.TestCase):
    def test_hex_decode(self):
        self.assertEqual(['0xaa', '0xab'], hex_decode([0xaa, 0xab]))


if __name__ == '__main__':
    unittest.main()
