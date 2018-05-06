import unittest

from PPI import *
import numpy as np


class TestPPI(unittest.TestCase):
    def test_amplitudes(self):
        a = [0.1, 0.2, 0.3, 0.4, 0.1, 0.8, -0.5, 0]
        np.allclose([0.1, 0.1, 0.1, 0.3, 0.7, 1.3, 0.5], PPI.get_amplitudes(a))

    def test_ppi(self):
        all = [0.1, 0.2, 0.3, 0.4, 0.1, 0.8, -0.5, 0]
        filtered = [0.3, 0.4, 0.1, 0.8]
        np.allclose([0.1, 0.1, 0.1, 0.3, 0.7, 1.3, 0.5], PPI.get_amplitudes(all))
        np.allclose([0.1, 0.3, 0.7], PPI.get_amplitudes(filtered))
        self.assertEqual(0.44285714285714295, np.average(PPI.get_amplitudes(all)))
        self.assertEqual(0.3666666666666667, np.average(PPI.get_amplitudes(filtered)))

        ppi = (0.3666666666666667 - 0.44285714285714295) / 0.3666666666666667

        self.assertEqual((0.3666666666666667, 0.44285714285714295, ppi), PPI.get_ppi(all, filtered))


if __name__ == '__main__':
    unittest.main()
