""" Реализация собственно игрового движка """

import random

from game import const
from game.helpers import GameException, Player, Deal, Card, TableItem


class Engine(object):

    def __init__(self, players:list, bet:int, **options):
        # игроки и опции игры
        self.players = players                                          # список игроков, экземпляры Player
        self._bet = bet                                                 # ставка на игру (стоимость одного очка в копейках)
        self._deal_types = set(options['deal_types'])                   # типы раздач, учавствующих в игре (const.DEAL_...)
        self._game_sum_by_diff = options['game_sum_by_diff']            # переключить подведение итогов игры: по разнице между игроками (True) или по старшим очкам, что жопистее (False)
        self._dark_allowed = options['dark_allowed']                    # вкл/выкл возможность заказывать в темную (в обычных раздачах)
        self._third_pass_limit = options['third_pass_limit']            # вкл/выкл ограничение на 3 паса подряд
        self._no_joker = options['no_joker']                            # игра без джокеров вкл/выкл
        self._strong_joker = options['strong_joker']                    # джокер играет строго по масти или нет (берет козыря, когда выдан за некозырную масть или нет)
        self._joker_demand_peak = options['joker_demand_peak']          # джокер может/нет требовать "по старшей/младшей карте масти"

        # параметры для расчета очков
        self._base_fail_coef = -1                                       # базовый коэффициент для не взятой (недобора), мизера и прочих минусов (минусующий)
        self._fail_subtract_all = options['fail_subtract_all']          # способ расчета при недоборе: True - минусовать весь заказ / False - минусовать только недостающие (разницу между заказом и взятыми)
        self._pass_factor = options['pass_factor']                      # очки за сыгранный пас
        self._take_factor = 10                                          # очки за сыгранную взятку в обычной игре
        self._gold_mizer_factor = options['gold_mizer_factor']          # очки за взятку на золотой/мизере
        self._dark_notrump_factor = options['dark_notrump_factor']      # очки за сыгранную взятку на темной/бескозырке
        self._brow_factor = options['brow_factor']                      # очки за сыгранную взятку на лобовой
        self._dark_mult = options['dark_mult']                          # множитель для темной

        # всякие штрафы/бонусы
        self._gold_mizer_on_null = options['gold_mizer_on_null']        # вкл/выкл штраф/бонус за 0 взяток на золоте/мизере
        self._on_all_order = options['on_all_order']                    # вкл/выкл бонус/штраф, если заказ = кол-ву карт в раунде и взял/не взял
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
        self._trump_card = None         # карта, которая лежит в качестве козыря
        self._is_bet = True             # определяет тип хода в круге - заказ (true) или ход картой (false)
        self._to_next_deal = True       # флаг, что нужно перейти к следующей раздаче в процедуре next
        self._to_next_lap = False       # флаг, что нужно перейти к следующему кругу в процедуре next
        self._take_player = None        # игрок, забравший взятку
        self._released_cards = []       # массив вышедших карт (для ИИ)
        self._status = None             # текущий статус для внешних интерфейсов (Заказ ИИ, Ожидание заказа человека, ход ии и т.д.)

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
            if i >= self.party_size() - 1:
                i = 0
            else:
                i += 1

    def _order_table(self):
        """ Возвращает эл-ты игрового стола [(player_idx, TableItem()), ...] в порядке, в котором ходили, в виде списка """
        return sorted(self._table.items(), key=lambda x: x[1].order)

    def _reset(self):
        """ Сброс состояния внутренних переменных до начального """
        self._started = False
        self._status = const.EXT_STATE_DEAL
        self._game_record = []
        self._deals = []
        self._step = -1
        self._curr_deal = -1
        self._table = {}
        self._curr_player = None
        self._trump = None
        self._trump_card = None
        self._is_bet = True
        self._to_next_deal = True
        self._to_next_lap = False
        self._take_player = None
        self._released_cards = []

    def _init_record(self):
        """ Инициализирует таблицу игровых результатов, добавляет в нее одну строку - шапку """

        cap = {}

        for p in self._players:
            cap[p.id] = {'order': 'Заказ', 'take': 'Взято', 'scores': 'Очки', 'total': 'Счет'}

        self._game_record.append(cap)

    def _init_deals(self):
        """ Формирование очереди раздач на всю партию """

        # Первым ходящим выбирается случайный игрок, а далее все по кругу
        player_idx = random.randint(0, self.party_size() - 1)
        max_player_cards = round(36 / self.party_size())

        for dt in self._deal_types:
            if dt == const.DEAL_NORMAL_ASC:
                for n in range(1, max_player_cards):
                    self._deals.append(Deal(player_idx, dt, n))
                    player_idx = self._inc_index(player_idx, self.party_size())
            elif dt == const.DEAL_NORMAL_DESC:
                for n in range(max_player_cards - 1, 0, -1):
                    self._deals.append(Deal(player_idx, dt, n))
                    player_idx = self._inc_index(player_idx, self.party_size())
            else:
                for n in range(1, len(self._players) + 1):
                    self._deals.append(Deal(player_idx, dt, 1 if dt == const.DEAL_BROW else max_player_cards))
                    player_idx = self._inc_index(player_idx, self.party_size())

    def _deal_cards(self):
        """ Процедура раздачи карт в начале раунда + сброс некоторых переменных для нового раунда """

        if not self._started:
            return

        self._curr_deal += 1
        self._to_next_deal = False
        self._to_next_lap = False
        self._trump_card = None

        deal = self._deals[self._curr_deal]
        self._take_player = None
        self._curr_player = deal.player
        self._is_bet = deal.type_ not in (const.DEAL_MIZER, const.DEAL_GOLD)

        # сформируем колоду для раздачи
        deck = [Card(l, v, is_joker=v == 7 and l == const.LEAR_SPADES and not self._no_joker) for l in range(4) for v in range(6, 15)]
        # перетасуем колоду
        random.shuffle(deck)

        # выберем козырь (тянем случайную карту из колоды)
        if deal.type_ == const.DEAL_NO_TRUMP:
            self._trump = const.LEAR_NOTHING
        else:
            card = random.randrange(len(deck))

            if deck[card].joker and not self._no_joker:
                # если вытянули джокера - то бескозырка
                self._trump = const.LEAR_NOTHING
            else:
                self._trump = deck[card].lear

            if deal.cards < 36 / self.party_size():
                # если раздаем не всю колоду, надо запомнить козырную для ИИ и убрать ее из колоды,
                # т.к. по правилам она кладется на стол и никому попасть не должна
                self._released_cards.append(deck[card])
                self._trump_card = deck.pop(card)

        # ну а теперь собственно раздадим карты, начинаем раздавать с первого игрока (определенного случайно при инициализации раздач)
        for _ in range(deal.cards):
            for player, pidx, last in self._enum_players(deal.player):
                player.cards.append(deck.pop(0))

        # сделаем базовую сортировку карт, это для примитивных клиентов
        for p in self._players:
            p.cards = sorted([c for c in p.cards], key=lambda x: (x.lear, x.value), reverse=True)

    def _calc_scores(self, player:Player):
        """ Расчет очков за раунд у игрока """

        scores = 0
        detailed = []
        deal_type = self._deals[self._curr_deal].type_
        block_end = self._curr_deal == len(self._deals) - 1 or \
                    self._deals[self._curr_deal].type_ != self._deals[self._curr_deal + 1].type_

        # определяем базовый множитель за взятку
        if deal_type in (const.DEAL_NORMAL_ASC, const.DEAL_NORMAL_FULL, const.DEAL_NORMAL_DESC):
            take_factor = self._take_factor
        elif deal_type in (const.DEAL_NO_TRUMP, const.DEAL_DARK):
            take_factor = self._dark_notrump_factor
        elif deal_type in (const.DEAL_GOLD, const.DEAL_MIZER):
            take_factor = self._gold_mizer_factor
        elif deal_type == const.DEAL_BROW:
            take_factor = self._brow_factor

        # считаем базовые очки
        if deal_type in (const.DEAL_GOLD, const.DEAL_MIZER):
            scores = player.take * take_factor
        elif player.take == player.order:
            player.success_counter += 1
            if player.take == 0:
                scores = self._pass_factor
            else:
                scores = player.take * take_factor
        elif player.take > player.order:
            scores = player.take
        elif player.take < player.order:
            if self._fail_subtract_all:
                scores = player.order * take_factor
            else:
                scores = (player.order - player.take) * take_factor

        # умножить, если заказ в темную
        if deal_type == const.DEAL_DARK or player.order_is_dark:
            scores *= self._dark_mult

        # дополнительные бонусы/штрафы
        # за заказ равный кол-ву карт в раздаче (кроме случаев, когда раздается одна карта)
        if self._on_all_order and deal_type not in (const.DEAL_GOLD, const.DEAL_MIZER, const.DEAL_BROW) and \
            player.order == self._deals[self._curr_deal].cards and self._deals[self._curr_deal].cards > 1:
            scores *= 2

        detailed.append(scores)

        # за 0 взяток на золотой/мизере
        if self._gold_mizer_on_null and deal_type in (const.DEAL_GOLD, const.DEAL_MIZER) and player.take == 0:
            x = take_factor * 5
            scores += x
            detailed.append(x)

        # Доп. бонус за то, что успешно сыграл все игры блока
        if self._take_block_bonus and deal_type not in (const.DEAL_NORMAL_ASC, const.DEAL_NORMAL_DESC) and block_end \
            and player.success_counter == self.party_size():
            x = take_factor * self.party_size() * (self._dark_mult if deal_type == const.DEAL_DARK or player.order_is_dark else 1)
            scores += x
            detailed.append(x)

        # минусуем итог, если недобор/мизер/причие минусующие условия
        if deal_type == const.DEAL_MIZER or (player.take < player.order and player.order > 0) or \
            (deal_type == const.DEAL_GOLD and self._gold_mizer_on_null and player.take == 0):
            scores *= self._base_fail_coef
            detailed[0] *= self._base_fail_coef

        if block_end:
            player.success_counter = 0

        return scores, detailed

    def _end_round(self):
        """ Завершение раунда, подведение итогов """

        # посчитать итоги раунда, записать в таблицу игры
        rec = {}

        for p in self._players:
            p.scores, detailed = self._calc_scores(p)
            p.total_scores += p.scores
            det_str = ' + '.join([str(s) for s in detailed]) if len(detailed) > 1 else ''
            scores_str = '{0}{1}'.format(p.scores, f' ({det_str})' if det_str else '')
            rec[p.id] = {'order': p.order, 'take': p.take, 'scores': scores_str, 'total': p.total_scores}

        self._game_record.append(rec)

        # обнулить переменные раунда
        self._table = {}
        self._released_cards = []

        for p in self._players:
            p.order = -1
            p.take = 0
            p.scores = 0
            p.cards = []
            p.order_cards = []
            p.order_is_dark = False

        # если это последняя раздача (на момент окончания раунда номер текущей раздачи еще не поднят, так что текущий номер
        # раздачи будет именно номером отыгранной раздачи) - завершаем игру
        if self._curr_deal >= len(self._deals) - 1:
            self.stop()

    def _check_order(self, order, is_dark=False):
        """
        Выполняет проверку, возможно ли игроку сделать такой заказ.

        :return bool, message (сообщение с причиной, почему заказ невозможен)
        """

        if order < 0:
            return False, 'Нельзя заказать отрицательное количество взяток'

        if order > self._deals[self._curr_deal].cards:
            return False, 'Нельзя заказать взяток больше, чем карт на руках'

        player = self._players[self._curr_player]

        # если заказывал в темную, проверить - разрешено или нет это в текущей игре
        if is_dark and not self._dark_allowed:
            return False, 'Возможность заказывать в темную запрещена в этой партии'

        # последний заказывающий не может заказать столько взяток, чтобы сумма всех заказов игроков была равна кол-ву карт на руках
        if (self._step == self.party_size() - 1) and (
            order + sum(p.order for p in self._players if p != player) == self._deals[self._curr_deal].cards):
                return False, 'Сумма заказов всех игроков не может быть равна количеству карт на руках'

        # если включена опция на ограничение трех пасов подряд, проверить
        if self._third_pass_limit and order == 0 and player.pass_counter >= 2:
            # только надо исключить ситуации, когда на руках одна карта и ты вобще ничего не можешь заказать из-за этого
            if not (self._deals[self._curr_deal].cards == 1 and self._step == self.party_size() - 1 and (
                sum(p.order for p in self._players if p != player) + 1 == 1)):
                return False, 'Запрещено заказывать 3 паса подряд'

        return True, None

    def _check_beat(self, card_index, **joker_opts):
        """ Проверка, может ли игрок покрыть этой картой (это для случаев именно последующих за первым ходов) """

        player = self._players[self._curr_player]
        card = joker_opts.get('card', player.cards[card_index])
        tbl_ordered = self._order_table()

        # если первый ход сделан джокером, проверим требование по старшей/младшей карте масти
        if tbl_ordered[0][1].is_joker:
            if tbl_ordered[0][1].joker_action == const.JOKER_TAKE_BY_MAX and card != player.max_card(tbl_ordered[0][1].card.lear) \
                and player.lear_exists(tbl_ordered[0][1].card.lear):
                return False, f'Вы обязаны положить самую большую {const.LEAR_NAMES[tbl_ordered[0][1].card.lear]}'
            if tbl_ordered[0][1].joker_action == const.JOKER_TAKE_BY_MIN and card != player.min_card(tbl_ordered[0][1].card.lear) \
                and player.lear_exists(tbl_ordered[0][1].card.lear):
                return False, f'Вы обязаны положить самую маленькую {const.LEAR_NAMES[tbl_ordered[0][1].card.lear]}'

        # Если масть карты не совпадает с мастью первой на столе/заказанной джокером, проверить, может ли игрок кинуть эту масть
        if card.lear != tbl_ordered[0][1].card.lear:
            if player.lear_exists(tbl_ordered[0][1].card.lear):
                return False, f'Вы обязаны положить {const.LEAR_NAMES[tbl_ordered[0][1].card.lear]}'
            elif player.lear_exists(self._trump) and card.lear != self._trump:
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
        self._step = 0
        self._started = True
        self._deal_cards()
        self.next()

    def stop(self):
        self._started = False

        # подведем итоги игры
        for p in self._players:
            # очки умножаем на ставку в копейках и делим на 100, чтоб получить в рублях - это базовый выигрыш по твоим очкам
            p.last_money = p.total_scores * self._bet / 100

        # теперь взаиморасчеты: если считаем по разнице, то каждый игрок получает со всех, у кого меньше разницу между их суммой.
        # Т.о. тут можно выити в плюс, даже если ты не выиграл;
        # если считаем по старшему, то каждый, кроме выигравшего, отдает разницу между своими очками и выигравшим, выигравшему, но ничего ни с кого получает.
        # Т.о. тут все в минусе и только выигравший в плюсе
        ordered = sorted([(i, p.last_money) for i, p in enumerate(self._players)], key=lambda x: x[1], reverse=True)

        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                diff = ordered[i][1] - ordered[j][1]
                self._players[ordered[i][0]].last_money += diff
                self._players[ordered[j][0]].last_money -= diff

            if not self._game_sum_by_diff:
                break

        for p in self._players:
            p.total_money += p.last_money

    def next(self):
        if not self._started:
            return

        # если нужно перейти к следующему раунду
        if self._to_next_deal:
            if self._status == const.EXT_STATE_WALKS:
                self._status = const.EXT_STATE_LAP_PAUSE
            elif self._status == const.EXT_STATE_LAP_PAUSE:
                # сделать паузу, чтоб пользователь мог посмотреть результаты раунда
                self._status = const.EXT_STATE_ROUND_PAUSE
                self._end_round()
            elif self._status == const.EXT_STATE_ROUND_PAUSE:
                self._status = const.EXT_STATE_DEAL
                self._deal_cards()
                self.next()
            return

        if self._to_next_lap:
            # сделать паузу, чтоб пользователь мог посмотреть результаты круга
            self._status = const.EXT_STATE_LAP_PAUSE
            self._to_next_lap = False
            return
        else:
            if self._status == const.EXT_STATE_LAP_PAUSE:
                self._take_player = None
                self._table = {}
            self._status = const.EXT_STATE_WALKS

        # если текущий ход одного из игроков-людей - ничего не делаем, ждем передачи хода
        # (выполняется в процедуре give_walk, которая для человека будет дергаться извне)
        if not self._players[self._curr_player].is_robot:
            return

        if self._is_bet:
            # если сейчас этап заказов - делаем заказ и передаем ход следующему
            self.make_order(*self._ai_calc_order())
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
        if self._step == self.party_size() - 1:
            if self._is_bet:
                self._is_bet = False
            else:
                if len(self._players[self._curr_player].cards) == 0:
                    self._to_next_deal = True
                else:
                    self._to_next_lap = True

        if self._take_player is not None:
            self._curr_player = self._take_player
        else:
            self._curr_player = self._inc_index(self._curr_player, self.party_size())

        self._step = self._inc_index(self._step, self.party_size())

    def make_order(self, order, is_dark=False):
        """
        Фиксация заказа игрока. Выполняет проверки, что такой заказ допустим и записывает его игроку, если все ОК.
        Если не ОК - вызывает исключение
        """

        can_make, cause = self._check_order(order, is_dark)

        if not can_make:
            raise GameException(cause)

        player = self._players[self._curr_player]
        player.order = order
        player.order_is_dark = is_dark

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

        if self._step == self.party_size() - 1:
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

    def started(self):
        return self._started

    def current_deal(self):
        return self._deals[self._curr_deal]

    def trump(self):
        return self._trump, self._trump_card

    def table(self):
        return self._table

    def walk_player(self):
        """ Кто сейчас ходит """
        return self._curr_player, self.players[self._curr_player]

    def take_player(self):
        """ Кто взял в круге """
        return self._take_player, self.players[self._take_player]

    def status(self):
        return self._status

    def is_bet(self):
        return self._is_bet

    def get_record(self):
        """ Таблица игры """
        return self._game_record

    def party_size(self):
        return len(self._players)

    def lap_players_order(self, by_table=False):
        """ Возвращает список игроков, расположенных в порядке хода на текущем круге """
        if not by_table:
            return [(p, i) for p, i, b in self._enum_players(
                self._take_player if self._take_player is not None else self._deals[self._curr_deal].player)]
        else:
            return [(self._players[x[0]], x[0]) for x in self._order_table()]

    @property
    def dark_allowed(self):
        return self._dark_allowed

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, players:list):
        if len(players) < 3:
            raise GameException('Недостаточно игроков для начала игры! Количество игроков не может быть меньше 3-х')

        if len(players) > 35:
            raise GameException('Игроков не может быть больше кол-ва карт в колоде - 1 (на козыря), т.е. 35!')

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
        Расчитывает заказ на текущий раунд. Возвращает кол-во взяток, которые предполагает взять и в темную делается заказ или нет.
        Заполняет у игрока массив карт, на которые рассчитывает взять
        """

        player = self._players[self._curr_player]
        can = False
        coef = 0
        coef2 = 1

        while not can:
            # учесть еще уровень риска
            is_dark = self._deals[self._curr_deal].type_ == const.DEAL_DARK or (random.randint(0, 100) < 10 if self._dark_allowed else False)

            if is_dark:
                cnt = random.randint(0, round(len(player.cards) / 2) + 1)
            else:
                cnt = 0 + coef

                # если карт меньше 5, то на Т К Д не козырных заказываем сразу, на козырных + В 10
                # сразу не глядя прикрыта или нет. В бескозырке В 10 если только прикрыты
                # это для среднего уровня риска, остальные соотв. +1/-1
                limit = 11

                for c in player.cards:
                    if (c.value > limit) or (c.lear == self._trump and c.value + 2 > limit):  # + заказ на джокера
                        player.order_cards.append(c)
                        cnt += 1

            can, _ = self._check_order(cnt, is_dark)

            if not can:
                if cnt >= len(player.cards):
                    coef2 = -1  # еще доп. учесть +/- в зависимости от уровня риска

                coef += coef2

        return cnt, is_dark

    def _ai_calc_walk(self) -> int:
        """
        Вычисляет, чем походить. Для случаев, когда ходишь первый. Возвращает индекс карты в массиве карт игрока.
        Если выберет джокера, то вернет объект, содержащий индекс карты и действия по джокеру: действие, за какую карту выдает,
        требования, если есть. Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        player = self._players[self._curr_player]

        # Т.к. карты уже отсортированы по убыванию, задача упрошается
        # вобще надо будет сделать у игрока методы, возвращающие мин и макс карты без учета масти, чисто по значениям
        if self._curr_deal == const.DEAL_GOLD or (self._curr_deal != const.DEAL_GOLD and player.order != player.take):
            # или еще не набрал или уже перебрал - надо брать
            cands = [(i, c) for i, c in enumerate(player.cards) if c in player.order_cards]

            if not cands:
                cands = [(i, c) for i, c in enumerate(player.cards)]

            idx = cands[0][0]
        else:
            # взято свое - надо скинуть
            idx = [(i, c) for i, c in enumerate(player.cards)][-1][0]

        # idx = random.randint(0, len(player.cards) - 1)

        joker_opts = {}  # пока так
        # joker_opts = {
        #     'card': Card(self._trump if self._trump != const.LEAR_NOTHING else const.LEAR_HEARTS, 14),
        #     'action': const.JOKER_BIGEST
        # } if player.cards[idx].joker and not self._no_joker else {}

        return idx, joker_opts

    def _ai_calc_beat(self) -> int:
        """
        Вычисляет, чем покрыть карты на столе. Для случаев, когда ходишь НЕ первый. Возвращает индекс карты в массиве карт игрока.
        Если выберет джокера, то вернет объект, содержащий индекс карты и действия по джокеру: действие, за какую карту выдает,
        требования, если есть. Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        player = self._players[self._curr_player]
        tbl_ordered = self._order_table()
        can = False
        iter_limit = 100

        while not can:
            # idx = random.randint(0, len(player.cards) - 1)

            if self._curr_deal == const.DEAL_GOLD or (self._curr_deal != const.DEAL_GOLD and player.order != player.take):
                # или еще не набрал или уже перебрал - надо брать
                c = player.max_card(tbl_ordered[0][1].card.lear)
                if not c:
                    c = player.max_card(self._trump)
                if not c and iter_limit > 0:
                    ccc = [c for c in player.cards if c not in player.order_cards]
                    c = random.choice([c for c in ccc]) if ccc else None
                    iter_limit -= 1
                if not c:
                    c = random.choice([c for c in player.cards])
            else:
                # свое взято - надо сливать
                c = player.min_card(tbl_ordered[0][1].card.lear)
                if not c:
                    c = player.min_card(self._trump)
                if not c:
                    c = random.choice([c for c in player.cards])

            joker_opts = {}  # пока так
            # joker_opts = {
            #     'card': Card(self._trump if self._trump != const.LEAR_NOTHING else const.LEAR_HEARTS, 14),
            #     'action': const.JOKER_BIGEST
            # } if player.cards[idx].joker and not self._no_joker else {}

            idx = player.cards.index(c)
            can, _ = self._check_beat(idx, **joker_opts)

        return idx, joker_opts
