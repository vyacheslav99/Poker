import secrets
import string
import random
import threading
import time

from typing import Optional

from core import const


def int_size():
    return len((99).to_bytes(((99).bit_length() + 7) // 8, 'big'))


def int_to_bytes(number):
    return number.to_bytes((number.bit_length() + 7) // 8, 'big')


def int_from_bytes(nb):
    return int.from_bytes(nb, 'big')


def sort_cards(cards: list, direction, lear_order):
    """
    Сортирует карты игрока по заданному направлению и по мастям.

    :param cards: список карт игрока
    :param direction: направления сортировака как в объекте params (0, 1)
    :param lear_order: список мастей, в котором надо выстроить
    :return list: Вернет новый список карт, отсортированный как надо
    """

    # Разберем по мастям, и в пределах кажой отсортируем в заданном порядке
    lears = {const.LEAR_SPADES: [], const.LEAR_CLUBS: [], const.LEAR_DIAMONDS: [], const.LEAR_HEARTS: []}
    result = []

    for card in cards:
        lears[card.lear].append(card)

    for lear in lear_order:
        result += sorted(lears[lear], key=lambda x: (x.value), reverse=direction == 1)

    return result


def gen_passwd(length=9):
    password = list(''.join([secrets.choice(string.ascii_uppercase) for _ in range(length // 3)]) +
                    ''.join([secrets.choice(string.ascii_lowercase) for _ in range(length // 3)]) +
                    ''.join([secrets.choice(string.digits) for _ in range(length-(length // 3 * 2))]))
    random.shuffle(password)
    password = ''.join(password)
    return password


class IntervalTimer:

    def __init__(self, interval: float, func: callable, *args, **kwargs):
        self._break = False
        self._interval = interval
        self._callback = func
        self._args = args
        self._kwargs = kwargs
        self._thread = threading.Thread(target=self._do_exec)
        self._thread.daemon = True
        self._thread.start()

    def _do_exec(self):
        while not self._break:
            time.sleep(self._interval)
            if not self._break:
                try:
                    self._callback(*self._args, **self._kwargs)
                except:
                    break

    def active(self):
        return self._thread.is_alive()

    def stop(self):
        self._break = True