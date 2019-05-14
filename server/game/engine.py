""" Реализация собственно игрового движка """

import random

from game import const
from game.helpers import GameException, Player, Deal, Card, TableItem


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
        self._joker_as_any_card = options['joker_as_any_card']          # джокер можно выдавать за любую карту или можешь только сказать "забираю/скидываю"

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
        self._on_all_order = options['on_all_order']                    # вкл/выкл бонус/штраф, если заказ = кол-ву карт в раунде и взял/не взял
        self._third_pass_limit = options['third_pass_limit']            # вкл/выкл ограничение на 3 паса подряд
        self._take_block_bonus = options['take_block_bonus']            # вкл/выкл приемию за сыгранные все раунды блока

        # переменные внутреннего состояния
        self._started = False
        self._game_record = []          # таблица с записью хода игры
        self._deals = []                # массив раздач
        self._step = -1                 # № шага (хода) в круге (шаг - это ход/заказ одного игрока, всего шагов 3 или 4 (по кол-ву игроков))
        self._curr_deal = -1            # индекс текущей раздачи в массиве раздач
        self._table = {}                # карты на столе, key: индекс игрока, value: TableItem
        self._curr_player = None        # игрок, чей сейчас ход
        self._trump = None              # козырная масть в текущем раунде
        self._is_bet = True             # определяет тип хода в круге - заказ (true) или ход картой (false)
        self._to_next_deal = True       # флаг, что нужно перейти к следующей раздаче в процедуре next
        self._can_stop = False          # флаг, что следующим ходом игра заканчивается
        self._take_player = None        # игрок, забравший взятку
        self._released_cards = []       # массив вышедших карт (для ИИ)

    def _inc_index(self, idx, max_val, increment=1):
        """
        Циклическое приращение индекса (начинает с начала, если достиг максимума). Полезно для перебора игроков например.
        Наращивает всегда по одному, проверяя на макс. значение каждый раз (даже если increment > 1).
        Что позволяет пройти несколько кругов приращения
        """

        for _ in range(increment):
            idx += 1
            if idx >= max_val:
                idx = 0

        return idx

    def _enum_players(self, start=0):
        """
        Функция-итератор. Перебирает игроков по кругу 1 раз, начиная от переданного индекса, заканчивая предыдущим ему

        :returns player:Player, index:int, is_last:bool
        """

        i = start

        for x in range(self.party_size()):
            yield self._players[i], i, x == self.party_size() - 1
            i += 1

            if i >= self.party_size() - 1:
                i = 0

    def _order_table(self):
        """ Возвращает эл-ты игрового стола [(player_idx, TableItem()), ...] в порядке, в котором ходили, в виде списка """
        return sorted(self._table.items(), key=lambda x: x[1].order)

    def _reset(self):
        """ Сброс состояния внутренних переменных до начального """
        self._started = False
        self._game_record = []
        self._deals = []
        self._step = -1
        self._curr_deal = -1
        self._table = {}
        self._curr_player = None
        self._trump = None
        self._is_bet = True
        self._to_next_deal = True
        self._can_stop = False
        self._take_player = None
        self._released_cards = []

    def _init_record(self):
        """ Инициализирует таблицу игровых результатов, добавляет в нее одну строку - шапку """

        cap = {}
        fields = {'order': 'Заказ', 'take': 'Взятки', 'scores': 'Очки', 'total': 'Счет'}

        for p in self._players:
            cap[f'{p.id}'] = fields

        self._game_record.append(cap)

    def _init_deals(self):
        """ Формирование очереди раздач на всю партию """

        # Первым ходящим выбирается случайный игрок, а далее все по кругу
        player_idx = random.randint(0, self.party_size())
        max_player_cards = 36 / self.party_size()

        for dt in self._deal_types:
            if dt == const.DEAL_NORMAL_ASC:
                for n in range(1, max_player_cards + 1):
                    self._deals.append(Deal(player_idx, dt, n))
                    player_idx = self._inc_index(player_idx, self.party_size())
            elif dt == const.DEAL_NORMAL_DESC:
                for n in range(max_player_cards, 0, -1):
                    self._deals.append(Deal(player_idx, dt, n))
                    player_idx = self._inc_index(player_idx, self.party_size())
            else:
                for n in range(1, len(self._players) + 1):
                    self._deals.append(Deal(player_idx, dt, 1 if dt == const.DEAL_BROW else max_player_cards))
                    player_idx = self._inc_index(player_idx, self.party_size())

    def _deal_cards(self):
        """ Процедура раздачи карт в начале раунда + сброс некоторых переменных для нового раунда """

        self._curr_deal += 1
        self._to_next_deal = False

        # если № раздачи превысил размер массива раздач - конец игре
        if self._curr_deal >= len(self._deals):
            self.stop()
            return

        deal = self._deals[self._curr_deal]
        self._take_player = None
        self._curr_player = deal.player
        self._is_bet = deal.type_ not in (const.DEAL_MIZER, const.DEAL_GOLD)

        # сформируем колоду для раздачи
        deck = [Card(l, v) for l in range(4) for v in range(6, 15)]
        # перетасуем колоду
        random.shuffle(deck)

        # выберем козырь (тянем случайную карту из колоды)
        if deal.type_ == const.DEAL_NO_TRUMP:
            self._trump = const.LEAR_NOTHING
        else:
            card = random.randrange(len(deck) + 1)

            if deck[card].joker:
                # если вытянули джокера - то бескозырка
                self._trump = const.LEAR_NOTHING
            else:
                self._trump = deck[card].lear

            if deal.cards < 36 / self.party_size():
                # если раздаем не всю колоду, надо запомнить козырную для ИИ и убрать ее из колоды,
                # т.к. по правилам она кладется на стол и никому попасть не должна
                self._released_cards.append(deck[card])
                deck.pop(card)

        # ну а теперь собственно раздадим карты, начинаем раздавать с первого игрока (определенного случайно при инициализации раздач)
        for _ in range(deal.cards):
            for player, pidx, last in self._enum_players(deal.player):
                player.cards.append(deck.pop(0))

    def _end_round(self):
        pass

    def _check_order(self, order):
        """
        Выполняет проверку, возможно ли игроку сделать такой заказ.

        :return bool, message (сообщение с причиной, почему заказ невозможен)
        """

        if order < 0:
            return False, 'Нельзя заказать отрицательное количество взяток'

        if order > self._deals[self._curr_deal].cards:
            return False, 'Нельзя заказать взяток больше, чем карт на руках'

        player = self._players[self._curr_player]

        # последний заказывающий не может заказать столько взяток, чтобы сумма всех заказов игроков была равна кол-ву карт на руках
        if (self._step == self.party_size() - 1) and (
            order + sum(p.order for p in self._players if p != player) == self._deals[self._curr_deal].cards):
                return False, 'Сумма заказов всех игроков не может быть равна количеству карт на руках'

        # если включена опция на ограничение трех пасов подряд, проверить
        if self._third_pass_limit and order == 0 and player.pass_counter >= 2:
            return False, 'Запрещено заказывать 3 паса подряд'

        return True, None

    def _check_beat(self, card_index, **joker_opts):
        """ Проверка, может ли игрок покрыть этой картой (это для случаев именно последующих за первым ходов) """

        player = self._players[self._curr_player]
        card = joker_opts.get('card', player.cards[card_index])
        tbl_ordered = self._order_table()

        # если первый ход сделан джокером, проверим требование по старшей/младшей карте масти
        if tbl_ordered[0][1].is_joker:
            if tbl_ordered[0][1].joker_action == const.JOKER_TAKE_BY_MAX and card != player.max_card(tbl_ordered[0][1].card.lear):
                return False, f'Вы обязаны положить самую большую {const.LEAR_NAMES[tbl_ordered[0][1].card.lear]}'
            if tbl_ordered[0][1].joker_action == const.JOKER_TAKE_BY_MIN and card != player.min_card(tbl_ordered[0][1].card.lear):
                return False, f'Вы обязаны положить самую маленькую {const.LEAR_NAMES[tbl_ordered[0][1].card.lear]}'

        # Если масть карты не совпадает с мастью первой на столе/заказанной джокером, проверить, может ли игрок кинуть эту масть
        if card.lear != tbl_ordered[0][1].card.lear:
            if player.lear_exists(tbl_ordered[0][1].card.lear):
                return False, f'Вы обязаны положить {const.LEAR_NAMES[tbl_ordered[0][1].card.lear]}'
            elif player.lear_exists(self._trump):
                return False, f'Вы обязаны положить козыря'

        return True, None

    def _compare_cards_ti(self, card_low:TableItem, card_top:TableItem):
        """
        Определяет, какая из 2-х карт побила. Первой считается card_low, а card_top та, что ложат сверху.
        Вернет True, если побила card_top, False - если бьет card_low.
        """

        if card_low.card.lear == card_top.card.lear:
            # Если масти одинаковые, победила та, которая больше
            if card_top.card.value > card_low.card.value:
                return True
            elif card_top.card.value < card_low.card.value:
                return False
            else:
                # карты равны - значит одна из них джокер - она и бьет
                return card_top.is_joker
        else:
            # Если масти разные, бьет козырная, а если ее нет - то card_low (т.к. ей ходили, а card_top - крыли)
            return card_top.card.lear == self._trump

    def start(self):
        self._reset()
        self._init_record()
        self._init_deals()
        self._deal_cards()
        self._step = 0
        self._started = True
        self.next()

    def stop(self):
        if self._started:
            self._reset()

    def next(self):
        if self._can_stop:
            return

        # если нужно перейти к следующему раунду
        if self._to_next_deal:
            self._end_round()
            self._deal_cards()
            self.next()
            return

        # если текущий ход одного из игроков-людей - ничего не делаем, ждем передачи хода
        # (выполняется в процедуре give_walk, которая для человека будет дергаться извне)
        if not self._players[self._curr_player].is_robot:
            return

        if self._is_bet:
            # если сейчас этап заказов - делаем заказ и передаем ход следующему
            self.make_order(self._ai_calc_order())
        else:
            # сейчас этап ходов - делаем ход
            if self._step == 0:
                card_idx, joker_opts = self._ai_calc_walk()
            else:
                card_idx, joker_opts = self._ai_calc_beat()

            self.do_walk(card_idx, **joker_opts)

        # передаем ход следующему игроку, и сразу ходим им
        self.give_walk()
        self.next()

    def give_walk(self):
        """ передача хода следующему игроку """

        # если это последний шаг (игрок) в круге - переходим к следующему этапу (к ходам, если это был заказ,
        # к следующему кругу, или к следующей партии)
        if self._step == self.party_size():
            if self._is_bet:
                self._is_bet = False
            else:
                if len(self._players[self._curr_player].cards) == 0:
                    self._to_next_deal = True

        if self._take_player is not None:
            self._curr_player = self._take_player
        else:
            self._curr_player = self._inc_index(self._curr_player, self.party_size())

        self._step = self._inc_index(self._step, self.party_size())

    def make_order(self, order):
        """
        Фиксация заказа игрока. Выполняет проверки, что такой заказ допустим и записывает его игроку, если все ОК.
        Если не ОК - вызывает исключение
        """

        can_make, cause = self._check_order(order)

        if not can_make:
            raise GameException(cause)

        player = self._players[self._curr_player]
        player.order = order

        # актуализировать счетчик пасов
        if order == 0:
            player.pass_counter += 1
        else:
            player.pass_counter = 0

    def do_walk(self, card_index, **joker_opts):
        """ Выполнить действия хода картой. Если это не первый ход, выполнить предварительно проверки на возможность такого хода """

        # сначала проверки
        if self._step > 0:
            res, msg = self._check_beat(card_index, **joker_opts)
            if not res:
                raise GameException(msg)

        # осуществляем ход: извелечем карту у игрока, добавим в массивы вышедших и на стол
        player = self._players[self._curr_player]
        card = player.cards.pop(card_index)
        self._table[self._curr_player] = TableItem(self._step, joker_opts.get('card', card),
                                                   is_joker=len(joker_opts) > 0, joker_action=joker_opts.get('action'))
        self._released_cards.append(card)

        if self._step == self.party_size():
            # определяем, кто побил
            tbl_ordered = self._order_table()

            for i, item in enumerate(tbl_ordered):
                if i == 0:
                    self._take_player, max_card = item
                else:
                    if self._compare_cards_ti(max_card, item[1]):
                        self._take_player, max_card = item

            # запишем побившему +1 взятку
            self._players[self._take_player].take += 1

    def prepare_joker(self, joker_card, joker_action):
        """
        Внешний метод для обработки опций джокера, прилетающих от клиента.
        Преобразование в joker_opts и подбор карты для случаев, когда сказал - самая большая/маленькая и карту не назвал.
        Подбор происходит согласно договоренностей на игру по поведению джокера
        """
        pass

    def party_size(self):
        return len(self._players)

    @property
    def players(self):
        return self._players

    @property.setter
    def set_players(self, players:list):
        if len(players) < 3:
            raise GameException('Недостаточно игроков для начала игры! Количество игроков не может быть меньше 3-х')

        if len(players) > 4:
            raise GameException('Игроков не может быть больше 4!')

        c = len(players)
        for player in players:
            if player.is_robot:
                c -= 1

        if c == 0:
            raise GameException('В игру не добавлено ни одного игрока-человека!')

        self._players = players

    # --==** методы ИИ **==--

    def _ai_calc_order(self) -> int:
        """
        Расчитывает заказ на текущий раунд. Возвращает кол-во взяток, которые предполагает взять.
        Заполняет у игрока массив карт, на которые рассчитывает взять
        """

        pass

    def _ai_calc_walk(self) -> int:
        """
        Вычисляет, чем походить. Для случаев, когда ходишь первый. Возвращает индекс карты в массиве карт игрока.
        Если выберет джокера, то вернет объект, содержащий индекс карты и действия по джокеру: действие, за какую карту выдает,
        требования, если есть. Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        pass

    def _ai_calc_beat(self) -> int:
        """
        Вычисляет, чем покрыть карты на столе. Для случаев, когда ходишь НЕ первый. Возвращает индекс карты в массиве карт игрока.
        Если выберет джокера, то вернет объект, содержащий индекс карты и действия по джокеру: действие, за какую карту выдает,
        требования, если есть. Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        pass
