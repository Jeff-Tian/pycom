import struct

from helper import hex_decode

__all__ = ['PPI']


class PPI(object):
    @staticmethod
    def parse_gravity_data(data):
        print('data = ', hex_decode(data))
        try:
            # return struct.unpack('f', bytearray([data[12], data[11], data[10], 0x00]))[0]
            # return (data[10] - 0x0a) * 10  # (data[9] - 0xa)
            return (struct.unpack('L', bytearray([data[9], data[10], data[11], data[12]]))[0] * 2500 / (
                16777216 * 0.003833))
        except Exception as ex:
            print(ex)
            pass
