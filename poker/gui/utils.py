import  os


def int_size():
    return len((99).to_bytes(((99).bit_length() + 7) // 8, 'big'))


def int_to_bytes(number):
    return number.to_bytes((number.bit_length() + 7) // 8, 'big')


def int_from_bytes(nb):
    return int.from_bytes(nb, 'big')


def get_profile_dir():
    _dir = os.path.normpath(os.path.join(os.path.expanduser('~'), '.snake',))

    if not os.path.exists(_dir):
        os.makedirs(_dir, exist_ok=True)

    return _dir


def get_save_dir():
    _dir = os.path.join(get_profile_dir(), 'save')

    if not os.path.exists(_dir):
        os.makedirs(_dir, exist_ok=True)

    return _dir
