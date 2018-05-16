import struct
import traceback

from helper import hex_decode
import numpy as np

__all__ = ['PPI']


class PPI(object):
    @staticmethod
    def parse_gravity_data(data, base=0):
        try:
            ret = []
            for index in range(30):
                try:
                    item = [data[9 + index * 4], data[10 + index * 4], data[11 + index * 4], data[12 + index * 4]]
                    ret.append(PPI.parse_one_gravity_data(item, base))
                except:
                    ret.append(0)

            return ret
        except:
            print(traceback.format_exc())
            return [0 for i in range(30)]

    @staticmethod
    def parse_one_gravity_data(data, base=0):
        return (struct.unpack('L', bytearray(data))[0] * 2500 / (
            (2 ** 24) * 0.003833)) - base

    @staticmethod
    def get_amplitudes(data):
        data1 = data[0:-1]
        data2 = data[1:]

        return np.absolute(np.subtract(data1, data2))

    @staticmethod
    def get_ppi(full_data, filtered_data):
        # TODO: What if the p is zero?
        p = np.average(PPI.get_amplitudes(filtered_data))
        pp = np.average(PPI.get_amplitudes(full_data))
        ppi = (p - pp) / p

        return p, pp, ppi
