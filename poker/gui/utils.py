def int_size():
    return len((99).to_bytes(((99).bit_length() + 7) // 8, 'big'))


def int_to_bytes(number):
    return number.to_bytes((number.bit_length() + 7) // 8, 'big')


def int_from_bytes(nb):
    return int.from_bytes(nb, 'big')
