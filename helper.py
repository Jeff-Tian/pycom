__all__ = ['hex_decode', 'try_hex_encode']


def hex_decode(bytes):
    return [try_hex_encode(c) for c in bytes]


def try_hex_encode(c):
    try:
        return hex(c)
    except TypeError:
        return c
