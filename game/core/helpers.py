""" Вспомогательные классы, инкапсулирующие атрибуты логических единиц """

import random
from core import const


class GameException(Exception):
    pass


class Card(object):

    def __init__(self, lear:int, value:int, is_joker=False):
        self._lear = lear           # масть
        self._value = value         # достоинство, номинал
        self._is_joker = is_joker   # Джокер или нет (value == 7 and lear == const.LEAR_SPADES)

    @property
    def value(self):
        return self._value

    @property
    def lear(self):
        return self._lear

    @property
    def joker(self):
        return self._is_joker

    def __str__(self):
        if self.joker:
            return f'Joker ({const.CARD_NAMES[self._value]} {const.LEAR_SYMBOLS[self._lear]})'
        else:
            return f'{const.CARD_NAMES[self._value]} {const.LEAR_SYMBOLS[self._lear]}'


class TableItem(object):

    def __init__(self, order, card, is_joker=False, joker_action=None):
        self.order = order                  # Очередность хода, т.е. порядковый номер, которым была положена карта.
        self.card = card                    # Карта. Для игровой логики, т.е. если реально ходили джокером, то это та карта, за которую он выдан
        self.is_joker = is_joker            # Джокер это реально или нет. Если джокрер, то мы знаем, что реальная карта - 7 пик
        self.joker_action = joker_action    # Действие джокером, в т.ч. и требования джокера


class Player(object):

    def __init__(self, params=None):
        self.id = None
        self.login = None
        self.password = None
        self.name = None
        self.is_robot = None
        self.risk_level = None
        self.level = None

        # статистика
        self.total_money = 0            # сумма всех выигрышей
        self.total_games = 0            # +1 в начале игры
        self.completed_games = 0        # +1 при завершении игры (доведения игры до конца)
        self.interrupted_games = 0      # +1 при прерывании игры
        self.winned_games = 0           # +1 при выигрыше (набрал больше всех)
        self.failed_games = 0           # +1 при проигрыше (если ушел в минус)
        self.neutral_games = 0          # +1 если не выиграл и не проиграл (набрал не больше всех, но в плюсе)
        self.last_money = 0             # сумма последнего выигрыша

        # игровые переменные
        self.order = -1                 # заказ в текущем раунде
        self.take = 0                   # взято в текущем раунде
        self.scores = 0                 # очки в текущем раунде
        self.total_scores = 0           # общий счет в текущей игре на текущий момент
        self.cards = []                 # карты на руках
        self.order_cards = []           # карты, на которые сделан заказ (заполняется только у ИИ)
        self.order_is_dark = False      # текущий заказ был сделан в темную или нет
        self.pass_counter = 0           # счетчик пасов, заказанных подряд
        self.success_counter = 0        # счетчик успешно сыгранных подряд игр

        if params:
            self.from_dict(params)

    def from_dict(self, params):
        self.id = params['id']
        self.login = params['login']
        self.password = params['password']
        self.name = params['name']
        self.is_robot = params['is_robot']
        self.risk_level = params['risk_level']
        self.level = params['level']
        self.total_money = params['total_money']
        self.total_games = params['total']
        self.completed_games = params['completed']
        self.interrupted_games = params['interrupted']
        self.winned_games = params['winned']
        self.failed_games = params['failed']
        self.last_money = params['last_money']

    def as_dict(self):
        return {k: self.__dict__[k] for k in self.__dict__ if not k.startswith(self.__class__)}

    def lear_exists(self, lear):
        """ Проверяет, есть ли у игрока карты заданной масти. Вернет True/False """

        for card in self.cards:
            if not card.joker and card.lear == lear:
                return True

        return False

    def gen_lear_range(self, lear, ascending=False):
        """ Сформировать список карт игрока заданной масти, отсортированный в указанном порядке (по умолчанию убывание) """
        return sorted([card for card in self.cards if not card.joker and card.lear == lear],
                      key=lambda x: x.value, reverse=not ascending)

    def max_card(self, lear):
        """ Выдать максимальную карту заданной масти """
        lr = self.gen_lear_range(lear)
        return lr[0] if lr else None

    def min_card(self, lear):
        """ Выдать минимальную карту заданной масти """
        lr = self.gen_lear_range(lear, ascending=True)
        return lr[0] if lr else None

    def cards_sorted(self, ascending=False):
        """ Вернет список карт, отсортированный без учета масти в указанном порядке (по умолчанию убывание) """

        # предварительно перемешаем карты, чтобы масти каждый раз были в разном порядке. Это добавит элемент случайности
        mixed = [c for c in self.cards]
        random.shuffle(mixed)
        return sorted(mixed, key=lambda x: x.value, reverse=not ascending)

    def index_of_card(self, lear, value, joker=False):
        """ Ищет карту у игрока, возвращает ее индекс. Если joker==True - ищет по флагу joker, игнорируя масть и достоинство """

        for i, c in enumerate(self.cards):
            if (c.lear == lear and c.value == value) or (joker and c.joker):
                return i

        return -1

    def __str__(self):
        if self.is_robot:
            s = f'Робот <{const.DIFFICULTY_NAMES[self.level]}, {const.RISK_LVL_NAMES[self.risk_level]}>'
        else:
            s = 'Человек'

        return f'{self.name} ({s})'


class Deal(object):

    def __init__(self, player:Player, type_:int, cards:int):
        self.player = player    # первый ходящий в партии (НЕ РАЗДАЮЩИЙ! т.к. смысла его хранить нет - он нужен только для вычисления ходящего)
        self.type_ = type_      # тип раздачи
        self.cards = cards      # количество карт, раздаваемых одному игроку
