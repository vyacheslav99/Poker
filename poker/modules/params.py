import os
import json
import uuid
import random

from modules.base_model import BaseModel
from gui import const, utils
from modules.core import const as eng_const
from modules.core.helpers import Player


class Params(BaseModel):

    def __init__(self, filename=None, **kwargs):
        self.user = None
        self.color_theme = 'green'
        # Вариант колоды
        self.deck_type = random.choice(const.DECK_TYPE)
        # Вариант рубашки
        self.back_type = random.randint(1, 9)
        # Сортировка карт пр показе у игрока: 0: По возрастанию, 1: По убыванию
        self.sort_order = 0
        # Порядок расположения мастей
        self.lear_order = (eng_const.LEAR_SPADES, eng_const.LEAR_CLUBS, eng_const.LEAR_DIAMONDS, eng_const.LEAR_HEARTS)
        # Варианты начала игры:
        self.start_type = const.GAME_START_TYPE_ALL

        super(Params, self).__init__(filename, **kwargs)


class Options(BaseModel):

    def __init__(self, filename=None, **kwargs):
        self.game_sum_by_diff = True
        self.dark_allowed = False
        self.third_pass_limit = False
        self.fail_subtract_all = False
        self.no_joker = False
        self.joker_give_at_par = False
        self.joker_demand_peak = True
        self.pass_factor = 5
        self.gold_mizer_factor = 15
        self.dark_notrump_factor = 20
        self.brow_factor = 50
        self.dark_mult = 2
        self.gold_mizer_on_null = True
        self.on_all_order = True
        self.take_block_bonus = True
        self.bet = 10
        self.players_cnt = random.choice([3, 4])
        self.deal_types = [0, 1, 2, 3, 4, 5, 6]

        super(Options, self).__init__(filename, **kwargs)


class Profiles(BaseModel):

    def __init__(self, filename=None, **kwargs):
        self.__items = []
        super(Profiles, self).__init__(filename, **kwargs)

    def load(self, filename):
        """ Загрузка параметров из файла формата json """

        with open(filename, 'r') as f:
            profies = json.load(f)

        for profile in profies:
            self.__items.append(Player(**profile))

    def save(self, filename):
        """ Сохранение параметров в файл, в формате json """

        profiles = []
        for player in self.__items:
            profiles.append(player.as_dict())

        with open(filename, 'w') as f:
            json.dump(profiles, f)

    @property
    def profiles(self):
        return self.__items

    @profiles.setter
    def profiles(self, items: list):
        self.__items = items

    def get(self, uid) -> Player or None:
        for item in self.__items:
            if item.uid == uid:
                return item

        return None

    def get_item(self, uid):
        for i, item in enumerate(self.__items):
            if item.uid == uid:
                return i, item

        return -1, None

    def set_profile(self, profile: Player):
        i, item = self.get_item(profile.uid)

        if i > -1:
            self.__items[i] = profile
        else:
            self.__items.append(profile)

    def count(self):
        return len(self.__items)

    def create(self, **kwargs):
        """ Создать новый профиль и добавить его к списку """

        if 'uid' not in kwargs:
            kwargs['uid'] = uuid.uuid4().hex

        if 'login' not in kwargs:
            kwargs['login'] = f'{os.getlogin()}-{utils.gen_passwd(6).lower()}'

        if 'name' not in kwargs:
            kwargs['name'] = random.choice(const.HUMANS)

        if 'is_robot' not in kwargs:
            kwargs['is_robot'] = False

        self.__items.append(Player(**kwargs))
        return self.__items[-1]
