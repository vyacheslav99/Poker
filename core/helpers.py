""" Вспомогательные классы, инкапсулирующие атрибуты логических единиц """

import random

from core import const
from models.base_model import BaseModel
from models.player import Player


class GameException(Exception):
    pass


class Card(object):

    def __init__(self, lear: int, value: int, is_joker=False, joker_action=None, joker_lear=None):
        self._lear = lear                   # масть
        self._value = value                 # достоинство, номинал
        self._is_joker = is_joker           # Джокер или нет (value == 7 and lear == const.LEAR_SPADES)
        self.joker_action = joker_action    # Действие джокером. Реально задается в момент хода
        self.joker_lear = joker_lear        # Масть, запрошенная джокером. Реально задается в момент хода

    @property
    def value(self):
        return self._value

    @property
    def lear(self):
        return self._lear

    @property
    def joker(self):
        return self._is_joker

    def get_nominal_text(self):
        """ Вернуть сам номинал карты в текстовом представлении """
        return f'{const.CARD_NAMES[self._value]} {const.LEAR_SYMBOLS[self._lear]}'

    def __str__(self):
        if self.joker:
            return f'Джокер ({const.CARD_NAMES[self._value]} {const.LEAR_SYMBOLS[self._lear]})'
        else:
            return f'{const.CARD_NAMES[self._value]} {const.LEAR_SYMBOLS[self._lear]}'


class TableItem(object):

    def __init__(self, order, card: Card):
        self.order = order                  # Очередность хода, т.е. порядковый номер, которым была положена карта.
        self.card = card                    # Карта, которой ходили

    def is_joker(self):
        """ Флаг - джокер это или нет. Просто пробрасывает соответствующую опцию из карты """
        return self.card.joker

    def joker_action(self):
        """ Если джокер - то действие джокером. Просто пробрасывает соответствующую опцию из карты """
        return self.card.joker_action

    def joker_lear(self):
        """ Масть, запрошенная джокером. Просто пробрасывает соответствующую опцию из карты """
        return self.card.joker_lear


class Deal(object):

    def __init__(self, player: Player, type_: int, cards: int):
        self.player = player    # первый ходящий в партии (НЕ РАЗДАЮЩИЙ! т.к. смысла его хранить нет - он нужен только для вычисления ходящего)
        self.type_ = type_      # тип раздачи
        self.cards = cards      # количество карт, раздаваемых одному игроку


class StatisticItem(BaseModel):
    """ Показатели статистики по одному игроку за игровую партию """

    def __init__(self, filename=None, **kwargs):
        # базовые счетчики, на основе котоорых вычисляются рассчетные
        self.strength = None            # суммарная оценка розданных карт
        self.orders = None              # всего взяток заказано
        self.takes = None               # всего взяток взято
        self.win_games = None           # всего конов выиграно
        self.fail_games = None          # всего конов проиграно
        self.overage_games = None       # кол-во конов с перебором
        self.lack_games = None          # кол-во конов с недобором
        self.jokers = None              # количество джокеров
        self.joker_fail_games = None    # кол-во конов, проигранных с джокером на руках
        self.risky_games = None         # кол-во рискованных конов
        self.takes_on_mizer = None      # кол-во взяток на мизере
        self.zero_mizer_games = None    # кол-во конов на мизере с 0 взяток
        self.takes_on_gold = None       # кол-во взяток на золотых
        self.zero_gold_games = None     # кол-во золотых конов с 0 взяток
        self.dark_games = None          # кол-во конов в темную
        self.dark_orders = None         # кол-во заказов в темную
        self.dark_win_games = None      # кол-во выигранных конов в темную
        self.dark_fail_games = None     # кол-во проигранных конов в темную
        self.dark_overage_games = None  # кол-во конов с перебором на темных
        self.dark_lack_games = None     # кол-во конов с недобором на темных
        self.normal_dark_games = None   # кол-во конов в темную в обычных конах

        super(StatisticItem, self).__init__(filename, **kwargs)

    def win_vs_fail(self):
        """ Общее соотношение выигранных к проигранным (когда не взял заказ) конов """

    def order_vs_take(self):
        """ Общее соотношение заказов к взятому """


def flip_coin(probability, maximum=10):
    """
    Делает выбор ДА или НЕТ с заданной вероятностью в пользу ДА.

    :param probability: вероятность (число от 0 до maximum): сколько шансов из максимума должно быть в пользу ДА.
        Если probability == 0 - будет всегда НЕТ, если probability == maximum - всегда ДА
    :param maximum: Максимальное значение вероятности. Чем оно больше, тем точнее можно задать вероятность
    :return: bool - полученный ответ
    """

    if probability < 0 or probability > maximum:
        probability = round(maximum / 2)

    return random.choice([True for _ in range(probability)] + [False for _ in range(maximum-probability)])
