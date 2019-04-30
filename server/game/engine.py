""" Реализация собственно игрового движка """

from game import const
from game.helpers import GameException, Player


class Engine(object):

    def __init__(self, players:list, bet:float, **options):
        self.players = players                                          # список игроков, экземпляры Player
        self._bet = bet                                                 # ставка на игру (копеек)
        self._deal_types = set(options['deal_types'])                   # типы раздач, учавствующих в игре (const.DEAL_...)
        self._no_joker = options['no_joker']                            # игра без джокеров вкл/выкл
        self._strong_joker = options['strong_joker']                    # джокер играет строго по масти или нет (берет козыря, когда выдан за некозырную масть или нет)
        self._joker_major_lear = options['joker_major_lear']            # джокер может/нет требовать "по старшей карте масти"
        self._joker_minor_lear = options['joker_minor_lear']            # джокер может/нет требовать "по младшей карте масти"

        # параметры для расчета очков
        self._base_fail_coef = -1                                       # базовый коэффициент для не взятой (недобора), мизера и прочих минусов (минусующий)
        self._pass_factor = options['pass_factor']                      # очки за сыгранный пас
        self._take_factor = 10                                          # очки за сыгранную взятку в обычной игре
        self._gold_mizer_factor = options['gold_mizer_factor']          # очки за взятку на золотой/мизере
        self._dark_notrump_factor = options['dark_notrump_factor']      # очки за сыгранную взятку на темной/бескозырке
        self._brow_factor = options['brow_factor']                      # очки за сыгранную взятку на лобовой
        self._dark_mult = options['dark_mult']                          # множитель для темной
        self._brow_mult = options['brow_mult']                          # множитель для лобовой

        # всякие штрафы/бонусы
        self._gold_mizer_on_null = options['gold_mizer_on_null']        # вкл/выкл штраф/бонус за 0 взяток на золоте/мизере
        self._on_all_order = options['on_all_order']                    # вкл/выкл бонус/штраф, если заказ = кол-ву карт в раздаче и взял/не взял
        self._third_pass_limit = options['third_pass_limit']            # вкл/выкл ограничение на 3 паса подряд
        self._take_block_bonus = options['take_block_bonus']            # вкл/выкл приемию за сыгранные все игры блока

    @property
    def players(self):
        return self._players

    @property.setter
    def set_players(self, players:list):
        if len(players) < 3:
            raise GameException('Недостаточно игроков для начала игры!')

        if len(players) > 4:
            raise GameException('Игроков не может быть больше 4!')

        c = len(players)
        for player in players:
            if player.is_robot:
                c -= 1

        if c == 0:
            raise GameException('В игру не добавлено ни одного игрока-человека!')

        self._players = players

    def start(self):
        self._deals = []

    def stop(self):
        pass

    def next(self):
        pass
