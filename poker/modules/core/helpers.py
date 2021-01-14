""" Вспомогательные классы, инкапсулирующие атрибуты логических единиц """

import random
from . import const
from modules.base_model import BaseModel


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


class Player(BaseModel):

    __dump_keys = ['uid', 'login', 'name', 'avatar', 'is_robot', 'started', 'completed', 'throw', 'winned', 'lost',
                   'scores', 'money', 'last_scores', 'last_money', 'best_scores', 'best_money', 'worse_scores', 'worse_money']

    def __init__(self, filename=None, **kwargs):
        self.uid = None
        self.login = None
        self.password = None
        self.name = None
        self.avatar = None
        self.is_robot = None
        self.risk_level = None
        # self.level = None

        # общая статистика
        self.started = 0            # кол-во начатых игр (+1 в начале игры)
        self.completed = 0          # кол-во сыгранных игр (+1 при завершении игры)
        self.throw = 0              # кол-во брошенных партий (+1 когда бросаешь игру)
        self.winned = 0             # кол-во выигранных партий (+1 при выигрыше (набрал больше всех))
        self.lost = 0               # кол-во проигранных партий (+1 при проигрыше)
        self.scores = 0             # общий суммарный выигрыш (сумма очков всех сыгранных партий)
        self.money = 0.0            # общая сумма денег (сумма денег всех сыгранных партий)
        self.last_scores = 0        # последний выигрыш (очки)
        self.last_money = 0.0       # последний выигрыш (деньги)
        self.best_scores = 0        # лучший выигрыш (очки)
        self.best_money = 0.0       # лучший выигрыш (деньги)
        self.worse_scores = 0       # худший результат (очки)
        self.worse_money = 0.0      # худший результат (деньги)

        # игровые переменные
        self.order = -1                 # заказ в текущем раунде
        self.take = 0                   # взято в текущем раунде
        self.scores = 0                 # очки в текущем раунде
        self.total_scores = 0           # общий счет в текущей игре на текущий момент
        self.total_money = 0.0          # выигрыш в текущей игре (деньги)
        self.cards = []                 # карты на руках
        self.order_cards = []           # карты, на которые сделан заказ (заполняется только у ИИ)
        self.order_is_dark = False      # текущий заказ был сделан в темную или нет
        self.pass_counter = 0           # счетчик пасов, заказанных подряд
        self.success_counter = 0        # счетчик успешно сыгранных подряд игр

        super(Player, self).__init__(filename, **kwargs)

    def as_dict(self):
        return {k: self.__dict__[k] for k in self.__dict__ if k in self.__dump_keys}

    def lear_exists(self, lear):
        """ Проверяет, есть ли у игрока карты заданной масти. Джокер не учитывается. Вернет True/False """

        for card in self.cards:
            if not card.joker and card.lear == lear:
                return True

        return False

    def gen_lear_range(self, lear, ascending=False):
        """
        Сформировать список карт игрока заданной масти, отсортированный в указанном порядке (по умолчанию убывание).
        Джокер не включается в список
        """

        return sorted([card for card in self.cards if not card.joker and card.lear == lear],
                      key=lambda x: x.value, reverse=not ascending)

    def max_card(self, lear):
        """ Выдать максимальную карту заданной масти. Джокер не учитывается """
        lr = self.gen_lear_range(lear)
        return lr[0] if lr else None

    def min_card(self, lear):
        """ Выдать минимальную карту заданной масти. Джокер не учитывается """
        lr = self.gen_lear_range(lear, ascending=True)
        return lr[0] if lr else None

    def middle_card(self, lear):
        """ Выдает карту из середины заданной масти (со сдвигом к болшей, если поровну не делиться). Джокер не учитывается """

        lr = self.gen_lear_range(lear)

        if lr:
            if len(lr) > 1:
                return lr[round(len(lr) / 2) - 1]
            else:
                return lr[0]
        else:
            return None

    def cards_sorted(self, ascending=False):
        """ Вернет список карт, отсортированный без учета масти в указанном порядке (по умолчанию убывание) """

        # предварительно перемешаем карты, чтобы масти каждый раз были в разном порядке. Это добавит элемент случайности
        mixed = [c for c in self.cards]
        random.shuffle(mixed)
        return sorted(mixed, key=lambda x: x.value, reverse=not ascending)

    def index_of_card(self, lear=None, value=None, joker=False):
        """ Ищет карту у игрока, возвращает ее индекс. Если joker==True - ищет по флагу joker, игнорируя масть и достоинство """

        for i, c in enumerate(self.cards):
            if (c.lear == lear and c.value == value) or (joker and c.joker):
                return i

        return -1

    def card_exists(self, lear=None, value=None, joker=False, exclude_lear=None):
        """
        Смотрит, есть ли у игрока определенная карта.

        :param lear: Масть. Если не указать - будет искать карту указанного достоинства любой масти
        :param value: Достоинство. Можно опустить только если ищем джокера
        :param joker: флаг, что надо искать джокера: если True - ищет джокера, игнорируя масть и достоинство
        :param exclude_lear: исключая указанную масть
        """

        for c in self.cards:
            if (c.value == value and (c.lear == lear or lear is None) and (
                c.lear != exclude_lear or exclude_lear is None)) or (joker and c.joker):
                return True

        return False

    def add_to_order(self, cards):
        """ Добавить карты из списка к заказу """

        for c in cards:
            self.order_cards.append(c)

    def reset_game_variables(self):
        """ Сброс игровых переменных """

        self.order = -1
        self.take = 0
        self.scores = 0
        self.total_scores = 0
        self.total_money = 0.0
        self.cards = []
        self.order_cards = []
        self.order_is_dark = False
        self.pass_counter = 0
        self.success_counter = 0

    def assign_game_variables(self, source):
        """ Копирование игровых переменных из игрока-источника """

        self.order = source.order
        self.take = source.take
        self.scores = source.scores
        self.total_scores = source.total_scores
        self.total_money = source.total_money
        self.cards = source.cards
        self.order_cards = source.order_cards
        self.order_is_dark = source.order_is_dark
        self.pass_counter = source.pass_counter
        self.success_counter = source.success_counter

    def __str__(self):
        if self.is_robot:
            # s = f'Робот <{const.DIFFICULTY_NAMES[self.level]}, {const.RISK_LVL_NAMES[self.risk_level]}>'
            s = f'Робот <{const.RISK_LVL_NAMES[self.risk_level]}>'
        else:
            s = 'Человек'

        return f'{self.name} ({s})'


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
