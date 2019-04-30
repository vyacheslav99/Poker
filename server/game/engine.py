""" Реализация собственно игрового движка """

from game import const
from game.helpers import GameException, Player, Deal


class Engine(object):

    def __init__(self, players:list, bet:float, **options):
        # игроки и опции игры
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

        # переменные внутреннего состояния
        self._started = False
        self._game_record = []          # таблица с записью хода игры
        self._deals = []                # массив раздач
        self._step = 0                  # № шага в круге (шаг - это действие одного игрока, всего шагов 3 или 4 (по кол-ву игроков))
        self._curr_deal = -1            # индекс текущей раздачи в массиве раздач
        self._table = []                # карты на столе
        self._curr_player = None        # игрок, чей сейчас ход
        self._trump = None              # козырная масть
        self._is_bet = True             # какое сейчас действие - делаются ставки (true) или ходы (false)
        self._to_next_deal = True       # флаг, что нужно перейти к следующей раздаче в процедуре next
        # self._can_stop = False          # флаг, что следующим ходом игра заканчивается
        # self._prv_step = -1             # предыдущий шаг в круге
        # self._prv_deal = -1             # предыдущая раздача
        self._take_player = None        # игрок, забравший взятку
        self._released_cards = []       # массив вышедших карт (для ИИ)

    def _inc_index(self, idx, max_val, increment=1):
        idx += increment
        if idx == max_val:
            idx = 0

        return idx

    def _init_record(self):
        cap = {}
        fields = {'order': 'Заказ', 'take': 'Взятки', 'scores': 'Очки', 'total': 'Счет'}

        for p in self.players:
            cap[f'{p.id}'] = fields

        self._game_record.append(cap)

    def _init_deals(self):
        player_idx = 0

        for dt in self._deal_types:
            if dt == const.DEAL_NORMAL_ASC:
                for n in range(1, 37):
                    self._deals.append(Deal(player_idx, dt, n))
                    player_idx = self._inc_index(player_idx, len(self.players))
            elif dt == const.DEAL_NORMAL_DESC:
                for n in range(36, 0, -1):
                    self._deals.append(Deal(player_idx, dt, n))
                    player_idx = self._inc_index(player_idx, len(self.players))
            else:
                for n in range(1, len(self.players) + 1):
                    self._deals.append(Deal(player_idx, dt, 1 if dt == const.DEAL_BROW else 36))
                    player_idx = self._inc_index(player_idx, len(self.players))

    def _deal_cards(self):
        self._curr_deal += 1
        self._to_next_deal = False

        # если № раздачи превысил размер массива раздач - конец игре
        if self._curr_deal >= len(self._deals):
            self.stop()
            return

        self._take_player = None
        self._curr_player = self._deals[self._curr_deal].player
        #todo: тут я остановился

    def start(self):
        self._init_deals()
        self._init_record()
        self._deal_cards()
        self._started = True

    def stop(self):
        pass

    def next(self):
        pass

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
