import struct
import traceback

from helper import hex_decode

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
