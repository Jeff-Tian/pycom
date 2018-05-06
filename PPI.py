import struct
import traceback

from helper import hex_decode
import numpy as np

__all__ = ['PPI']


class PPI(object):
    @staticmethod
    def parse_gravity_data(data):
        try:
            return (struct.unpack('L', bytearray([data[9], data[10], data[11], data[12]]))[0] * 2500 / (
                16777216 * 0.003833))
        except:
            print(traceback.format_exc())
            return 0

    @staticmethod
    def get_amplitudes(data):
        data1 = data[0:-1]
        data2 = data[1:]

        return np.absolute(np.subtract(data1, data2))

    @staticmethod
    def get_ppi(full_data, filtered_data):
        p = np.average(PPI.get_amplitudes(filtered_data))
        pp = np.average(PPI.get_amplitudes(full_data))
        ppi = (p - pp) / p

        return p, pp, ppi
