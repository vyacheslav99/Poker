""" Вспомогательные классы, инкапсулирующие атрибуты логических единиц """

from game import const


class GameException(Exception):
    pass


class Deal(object):

    def __init__(self, player:Player, type_:int, cards:int):
        self.player = player
        self.type_ = type_
        self.cards = cards


class Player(object):

    id = None
    login = None
    password = None
    name = None
    is_robot = None
    risk_level = None
    level = None
    money = 0

    # статистика
    total_money = 0         # сумма всех выигрышей
    total_games = 0         # +1 в начале игры
    completed_games = 0     # +1 при завершении игры
    interrupted_games = 0   # +1 при прерывании игры
    winned_games = 0        # +1 при выигрыше (набрано больше всех)
    failed_games = 0        # +1 при проигрыше (не набрал больше всех)

    # игровые переменные
    order = 0               # заказ в текущем кругу
    take = 0                # взято в текущем кругу
    scores = 0              # очки в текущем кругу
    total_scores = 0        # общий счет в текущей игре на текущий момент
    cards = []              # карты на руках
    order_cards = []        # карты, на которые сделан заказ (только ИИ)

    def __init__(self, params=None):
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

    def as_dict(self):
        return {k: self.__dict__[k] for k in self.__dict__ if not k.startswith(self.__class__)}
