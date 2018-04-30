import struct

__all__ = ['PPI']


class PPI(object):
    @staticmethod
    def parse_gravity_data(data):
        try:
            return struct.unpack('f', bytearray([data[9], data[10], data[11], data[12]]))[0]
        except Exception as ex:
            print(ex)
            pass
