import os
import json
import uuid
import random

from domain.models.base_model import BaseModel
from domain.models.player import Player
from gui import const, utils
from core import const as eng_const


class Params(BaseModel):

    def __init__(self, filename=None, **kwargs):
        self.user = None
        # Цветовая тема оформления
        self.color_theme = 'green'
        # Графический стиль интерфейса
        self.style = 'Fusion'
        # Вариант колоды
        self.deck_type = random.choice(const.DECK_TYPE)
        # Вариант рубашки
        self.back_type = random.randint(1, 9)
        # Сортировка карт при показе у игрока: 0: По возрастанию, 1: По убыванию
        self.sort_order = 0
        # Порядок расположения мастей
        self.lear_order = (eng_const.LEAR_SPADES, eng_const.LEAR_CLUBS, eng_const.LEAR_DIAMONDS, eng_const.LEAR_HEARTS)
        # Варианты начала игры:
        self.start_type = const.GAME_START_TYPE_ALL
        # Игровая статистика локальных компьютерных игроков. key - имя, value - dict, представление RobotStatItem
        self.robots_stat = {}
        # Кастомные настройки оформления
        self.custom_decoration = const.DECORATION_THEMES['green'].copy()

        super(Params, self).__init__(filename, **kwargs)

        self.custom_decoration.update({k: v for k, v in const.DECORATION_THEMES['green'].items()
                                       if k not in self.custom_decoration})

    def _from_theme(self, param):
        return const.DECORATION_THEMES[self.color_theme].get(param, self.custom_decoration[param])

    def bg_texture(self):
        return self._from_theme(const.BG_TEXTURE)

    def bg_color(self):
        return self._from_theme(const.BG_COLOR)

    def bg_color_2(self):
        return self._from_theme(const.BG_COLOR_2)

    def bg_disabled(self):
        return self._from_theme(const.BG_DISABLED)

    def bg_dark_btn(self):
        return self._from_theme(const.BG_DARK_BTN)

    def bg_joker_lear_btn(self):
        return self._from_theme(const.BG_JOKER_LEAR_BTN)

    def color_main(self):
        return self._from_theme(const.COLOR_MAIN)

    def color_extra(self):
        return self._from_theme(const.COLOR_EXTRA)

    def color_extra_2(self):
        return self._from_theme(const.COLOR_EXTRA_2)

    def color_disabled(self):
        return self._from_theme(const.COLOR_DISABLED)

    def color_good(self):
        return self._from_theme(const.COLOR_GOOD)

    def color_bad(self):
        return self._from_theme(const.COLOR_BAD)

    def color_neutral(self):
        return self._from_theme(const.COLOR_NEUTRAL)

    def color_dark_btn(self):
        return self._from_theme(const.COLOR_DARK_BTN)

    def color_deal_normal(self):
        return self._from_theme(const.COLOR_DEAL_NORMAL)

    def color_deal_notrump(self):
        return self._from_theme(const.COLOR_DEAL_NOTRUMP)

    def color_deal_dark(self):
        return self._from_theme(const.COLOR_DEAL_DARK)

    def color_deal_gold(self):
        return self._from_theme(const.COLOR_DEAL_GOLD)

    def color_deal_mizer(self):
        return self._from_theme(const.COLOR_DEAL_MIZER)

    def color_deal_brow(self):
        return self._from_theme(const.COLOR_DEAL_BROW)

    def bg_player_1(self):
        return self._from_theme(const.BG_PLAYER_1)

    def color_player_1(self):
        return self._from_theme(const.COLOR_PLAYER_1)

    def bg_player_2(self):
        return self._from_theme(const.BG_PLAYER_2)

    def color_player_2(self):
        return self._from_theme(const.COLOR_PLAYER_2)

    def bg_player_3(self):
        return self._from_theme(const.BG_PLAYER_3)

    def color_player_3(self):
        return self._from_theme(const.COLOR_PLAYER_3)

    def bg_player_4(self):
        return self._from_theme(const.BG_PLAYER_4)

    def color_player_4(self):
        return self._from_theme(const.COLOR_PLAYER_4)


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

    def delete(self, uid):
        i, item = self.get_item(uid)

        if item:
            self.__items.pop(i)
            return True
        else:
            return False

    def count(self):
        return len(self.__items)

    def create(self, **kwargs):
        """ Создать новый профиль и добавить его к списку """

        self.__items.append(self.generate(**kwargs))

    def generate(self, **kwargs):
        """ Просто создать и вернуть новый профиль """

        if 'uid' not in kwargs:
            kwargs['uid'] = uuid.uuid4().hex

        if 'login' not in kwargs:
            kwargs['login'] = f'{os.getlogin()}-{utils.gen_passwd(6).lower()}'

        if 'name' not in kwargs:
            kwargs['name'] = random.choice(const.HUMANS)

        if 'is_robot' not in kwargs:
            kwargs['is_robot'] = False

        return Player(**kwargs)

    def filter(self, field, value):
        """
        Фильтрация по какому-то полю. Вернет список удовлетворяющих условию профилей.
        Проверяет только на полное совпадение, чувствителен к регистру.
        По мере надобности можно будет нарастить функционал, пока смысла нет.
        """

        return filter(lambda x: getattr(x, field) == value, self.__items)


class RobotStatItem(BaseModel):

    def __init__(self, filename=None, **kwargs):
        self.started = 0            # кол-во начатых игр (+1 в начале игры)
        self.completed = 0          # кол-во сыгранных игр (+1 при завершении игры)
        self.thrown = 0             # кол-во брошенных партий (+1 когда бросаешь игру)
        self.winned = 0             # кол-во выигранных партий (+1 при выигрыше (набрал больше всех))
        self.lost = 0               # кол-во проигранных партий (+1 при проигрыше)
        self.summary = 0            # общий суммарный выигрыш (сумма очков всех сыгранных партий)
        self.total_money = 0.0      # общая сумма денег (сумма денег всех сыгранных партий)
        self.last_scores = 0        # последний выигрыш (очки)
        self.last_money = 0.0       # последний выигрыш (деньги)
        self.best_scores = 0        # лучший выигрыш (очки)
        self.best_money = 0.0       # лучший выигрыш (деньги)
        self.worse_scores = 0       # худший результат (очки)
        self.worse_money = 0.0      # худший результат (деньги)

        super(RobotStatItem, self).__init__(filename, **kwargs)
