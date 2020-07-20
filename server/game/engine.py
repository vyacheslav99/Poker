""" Реализация собственно игрового движка """

import random

from . import const
from .helpers import GameException, Player, Deal, Card, TableItem, flip_coin


class Engine(object):

    def __init__(self, players: list, bet: int, **options):
        # игроки и опции игры
        self._allow_no_human = options.get('allow_no_human', False)     # разрешить игру без игроков-людей
        self._self_control = options.get('self_control', True)          # флаг, что игровой цикл (передача ходов и пр.) контролируется изнутри этого движка, иначе извне
        self.players = players                                          # список игроков, экземпляры Player
        self._bet = bet                                                 # ставка на игру (стоимость одного очка в копейках)
        self._deal_types = set(options['deal_types'])                   # типы раздач, учавствующих в игре (const.DEAL_...)
        self._game_sum_by_diff = options['game_sum_by_diff']            # переключить подведение итогов игры: по разнице между игроками (True) или по старшим очкам, что жопистее (False)
        self._dark_allowed = options['dark_allowed']                    # вкл/выкл возможность заказывать в темную (в обычных раздачах)
        self._third_pass_limit = options['third_pass_limit']            # вкл/выкл ограничение на 3 паса подряд
        self._no_joker = options['no_joker']                            # игра без джокеров вкл/выкл
        self._joker_give_at_par = options['joker_give_at_par']          # вариант сброса: True: по номиналу (как 7 пик), как самая маленькая заказанной масти
        self._joker_demand_peak = options['joker_demand_peak']          # джокер может/нет требовать "по старшей карте масти"

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
        self._released_lears = {}       # вышедшие у игроков масти (по данным анализа игры, не напрямую по игрокам)
        self._status = None             # текущий статус для внешних интерфейсов (Заказ ИИ, Ожидание заказа человека, ход ии и т.д.)

    def _inc_index(self, idx, max_val, increment=1):
        """
        Циклическое приращение индекса (начинает с начала, если достиг максимума). Нужно для перебора игроков например.
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
        self._released_lears = {}

    def _init_record(self):
        """ Инициализирует таблицу игровых результатов, добавляет в нее одну строку - шапку """

        cap = {}

        for p in self._players:
            cap[p.id] = {'order': 'Заказ', 'take': 'Взято', 'scores': 'Очки', 'total': 'Счет'}

        self._game_record.append(cap)

    def _init_released_lears(self):
        """ Инициализация массива вышедших мастей, делать в начале каждого раунда """

        for i in range(self.party_size()):
            self._released_lears[i] = set()

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
        self._init_released_lears()

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

            if deal.cards < round(36 / self.party_size()):
                # если раздаем не всю колоду, надо запомнить козырную для ИИ и убрать ее из колоды,
                # т.к. по правилам она кладется на стол и никому попасть не должна
                self._released_cards.append(deck[card])
                self._trump_card = deck.pop(card)

        # ну а теперь собственно раздадим карты, начинаем раздавать с первого игрока (определенного случайно при инициализации раздач)
        for _ in range(deal.cards):
            for player, pidx, last in self._enum_players(deal.player):
                player.cards.append(deck.pop(0))

        # сделаем базовую сортировку карт - небольшая предварительная оптимизация для анализаторов ИИ + для удобства работы клиентов
        # ну и вобще так удобнее работать. Сортировака по убыванию достоинства и масти
        for p in self._players:
            p.cards = sorted([c for c in p.cards], key=lambda x: (x.lear, x.value), reverse=True)

    def _calc_scores(self, player: Player):
        """ Расчет очков за раунд у игрока """

        scores = 0
        detailed = []
        deal_type = self._deals[self._curr_deal].type_
        block_end = self._curr_deal == len(self._deals) - 1 or deal_type != self._deals[self._curr_deal + 1].type_

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
        if self._on_all_order and deal_type not in (const.DEAL_GOLD, const.DEAL_MIZER, const.DEAL_BROW) \
            and player.order == self._deals[self._curr_deal].cards and self._deals[self._curr_deal].cards > 1:
            scores *= 2

        detailed.append(scores)

        # за 0 взяток на золотой/мизере
        if self._gold_mizer_on_null and deal_type in (const.DEAL_GOLD, const.DEAL_MIZER) and player.take == 0:
            x = take_factor * 5
            scores += x
            detailed.append(x)

        # Доп. бонус за то, что успешно сыграл все игры блока
        if self._take_block_bonus and deal_type not in (const.DEAL_NORMAL_ASC, const.DEAL_NORMAL_DESC, const.DEAL_BROW) \
            and block_end and player.success_counter == self.party_size():
            x = take_factor * self.party_size() * (self._dark_mult if deal_type == const.DEAL_DARK or player.order_is_dark else 1)
            scores += x
            detailed.append(x)

        # минусуем итог, если недобор/мизер/причие минусующие условия
        if (deal_type == const.DEAL_MIZER and player.take > 0) or (
            deal_type != const.DEAL_MIZER and player.take < player.order and player.order > 0) or (
            deal_type == const.DEAL_GOLD and self._gold_mizer_on_null and player.take == 0):
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
            rec[p.id] = {'order': f'{p.order}{"*" if p.order_is_dark else ""}', 'take': p.take, 'scores': scores_str, 'total': p.total_scores}

        self._game_record.append(rec)

        # обнулить переменные раунда
        self._table = {}
        self._released_cards = []
        self._released_lears = {}

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

    def _check_beat(self, card_index):
        """ Проверка, может ли игрок покрыть этой картой (это для случаев именно последующих за первым ходов) """

        player = self._players[self._curr_player]
        card = player.cards[card_index]
        tbl_ordered = self._order_table()
        required_lear = tbl_ordered[0][1].card.lear if not tbl_ordered[0][1].is_joker() else tbl_ordered[0][1].joker_lear()

        # если первый ход сделан джокером смотрим по джокеру
        if tbl_ordered[0][1].is_joker():
            # проверим требование по старшей карте, если оно включено
            if self._joker_demand_peak and tbl_ordered[0][1].joker_action() == const.JOKER_TAKE_BY_MAX and \
                card != player.max_card(required_lear) and player.lear_exists(required_lear):
                return False, f'Вы обязаны положить самую большую {const.LEAR_NAMES[required_lear]}'

        # Если масть карты не совпадает с мастью первой на столе/заказанной джокером, проверить, может ли игрок кинуть эту масть
        # в случае, если игрок ходит джокером - все можно, в т.ч. и кинуть масть не в попад
        if not card.joker and card.lear != required_lear:
            if player.lear_exists(required_lear):
                return False, f'Вы обязаны положить {const.LEAR_NAMES[required_lear]}'
            elif player.lear_exists(self._trump) and card.lear != self._trump:
                return False, f'Вы обязаны положить козырь'

        return True, None

    def _can_beat_card_ti(self, card_low:TableItem, card_top:TableItem):
        """
        Определяет, побъет ли карта card_top карту card_low. Первая card_low, card_top - та, что ложат сверху.
        Вернет True, если побила card_top, False - если бьет card_low.
        """

        return self._can_beat_card(card_low.card, card_top.card)

    def _can_beat_card(self, card_low:Card, card_top:Card):
        """
        Определяет, побъет ли карта card_top карту card_low. Первая card_low, card_top - та, что ложат сверху.
        Вернет True, если побила card_top, False - если бьет card_low.
        """

        # если нижняя джокер
        if card_low.joker:
            if card_low.joker_action in (const.JOKER_TAKE, const.JOKER_TAKE_BY_MAX):
                # если джокер забирает - джокер может не забрать, если заказана не козырная масть, а покрыли козырем
                return card_low.joker_lear != self._trump and card_top.lear == self._trump
            elif card_low.joker_action == const.JOKER_GIVE:
                # джокер скидывает
                if not self._joker_give_at_par:
                    # если сброс джокера происходит по номиналу - ничего не надо делать - кто побил выясниться дальше,
                    # а вот иначе надо сравнить
                    if card_low.joker_lear == card_top.lear:
                        # при одинаковых мастях джокер всегда самый маленький (т.е. берет верхняя)
                        return True
                    else:
                        # Если масти разные, бьет козырная, а если ее нет - то card_low (т.к. ей ходили, а card_top - крыли)
                        return card_top.lear == self._trump

        # если верхняя джокер
        if card_top.joker:
            if card_top.joker_action in (const.JOKER_TAKE, const.JOKER_TAKE_BY_MAX):
                # в данной ситуации джокер забирает всегда
                return True
            elif card_top.joker_action == const.JOKER_GIVE:
                # джокер скидывает
                if not self._joker_give_at_par:
                    # если сброс джокера происходит по номиналу - ничего не надо делать - кто побил выясниться дальше
                    # иначе джокер сливается в любом случае
                    return False

        # сравниваем просто по номиналу карт
        if card_low.lear == card_top.lear:
            # Если масти одинаковые, победила та, которая больше
            if card_top.value > card_low.value:
                return True
            elif card_top.value < card_low.value:
                return False
        else:
            # Если масти разные, бьет козырная, а если ее нет - то card_low (т.к. ей ходили, а card_top - крыли)
            return card_top.lear == self._trump

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

        # взаиморасчеты: если считаем по разнице, то каждый игрок получает разницу между cвоими очками и каждого другого.
        # Т.о. тут можно выити в плюс, даже если ты не выиграл;
        # если считаем по старшему, то каждый, кроме выигравшего, отдает разницу между своими очками и выигравшим, выигравшему, но ничего ни с кого получает.
        # Т.о. тут все в минусе и только выигравший в плюсе
        ordered = sorted([(i, p.total_scores) for i, p in enumerate(self._players)], key=lambda x: x[1], reverse=True)

        if self._game_sum_by_diff:
            for i in range(len(ordered)):
                for j in range(len(ordered)):
                    self._players[ordered[i][0]].last_money += ordered[i][1] - ordered[j][1]
        else:
            for i in range(len(ordered)):
                if i == 0:
                    self._players[ordered[i][0]].last_money += ordered[0][1]
                else:
                    self._players[ordered[i][0]].last_money += ordered[i][1] - ordered[0][1]

        # очки умножаем на ставку в копейках и делим на 100, чтоб получить в рублях - это базовый выигрыш по твоим очкам
        for p in self._players:
            p.last_money = p.last_money * self._bet / 100.0
            p.total_money += p.last_money

    def next(self):
        """ Центральный метод реализации игрового цикла """

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
                card_idx = self._ai_calc_walk()
            else:
                card_idx = self._ai_calc_beat()

            self.do_walk(card_idx)

        # передаем ход следующему игроку, и сразу ходим им
        self.give_walk()
        # у серверного варианта next всегда дергает диспетчер игры по своим соображениям
        if self._self_control:
            self.next()

    def give_walk(self):
        """ передача хода следующему игроку """

        # если это последний шаг (игрок) в круге - переходим к следующему этапу (к ходам, если это был заказ,
        # к следующему кругу, или раунду)
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

    def do_walk(self, card_index):
        """ Выполнить действия хода картой. Если это не первый ход, выполнить предварительно проверки на возможность такого хода """

        player = self._players[self._curr_player]

        # сначала проверки
        if self._no_joker and player.cards[card_index].joker:
            raise GameException('Игра джокером запрещена в этой партии')

        if self._step > 0:
            res, msg = self._check_beat(card_index)
            if not res:
                raise GameException(msg)

        # осуществляем ход: извелечем карту у игрока, добавим в массивы вышедших и на стол
        card = player.cards.pop(card_index)
        self._table[self._curr_player] = TableItem(self._step, card)
        self._released_cards.append(card)
        self._ai_walk_analyze(card)

        if self._step == self.party_size() - 1:
            # определяем, кто побил
            tbl_ordered = self._order_table()

            for i, item in enumerate(tbl_ordered):
                if i == 0:
                    self._take_player, max_card = item
                else:
                    if self._can_beat_card_ti(max_card, item[1]):
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
    def joker_give_at_par(self):
        return self._joker_give_at_par

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, players:list):
        if len(players) < 3:
            raise GameException('Недостаточно игроков для начала игры! Количество игроков не может быть меньше 3-х')

        if len(players) > 35:
            raise GameException('Игроков не может быть больше кол-ва карт в колоде - 1 (на козыря), т.е. 35!')

        if all((p.is_robot for p in players)) and not self._allow_no_human:
            raise GameException('В игру не добавлено ни одного игрока-человека! Реально хочешь посмотреть на битву машин?')

        self._players = players

    # --==** методы ИИ **==--

    def _ai_walk_analyze(self, card):
        """ Предварительный анализ карты, которой ходит игрок + сбор статистики ходов. Результаты будут использованы в алгоритмах ИИ """

        # определим, закончилась ли у игрока масть, которой заходили и если да, то запишем игроку в вышедшие масти
        # заодно можно вычислить, закончился ли козырь
        # На этом пока все :))
        if self._step > 0:
            _, tbl_item = self._order_table()[0]
            if tbl_item.card.lear != card.lear:
                # если походил не в масть - эта масть у него закончилась
                self._released_lears[self._curr_player].add(tbl_item.card.lear)

                # если еще и не козырем - значит и козрь закончился
                if self._trump != const.LEAR_NOTHING and card.lear != self._trump:
                    self._released_lears[self._curr_player].add(self._trump)

    def _ai_max_card(self, *cards):
        """ Определяет, какая из карт списка бьет. Учитывает порядок карт в списке. Возвращает побившую карту """

        max_card = None

        for i, card in enumerate(cards):
            if i == 0:
                max_card = card
            else:
                if self._can_beat_card(max_card, card):
                    max_card = card

        return max_card

    def _ai_greater_cards_released(self, card):
        """ Смотрит по вышедшим, вышли ли все карты крупнее переданной. Вернет True - если все, что больше, вышло, иначе - False """

        etalon = [i for i in range(card.value + 1, 15)]
        if not self._no_joker and card.lear == const.LEAR_SPADES and 7 in etalon:
            etalon.pop(etalon.index(7))

        return set(etalon) == set(
            (c.value for c in self._released_cards if c.lear == card.lear and c.value > card.value and not c.joker))

    def _ai_smallest_cards_released(self, card):
        """ Смотрит по вышедшим, вышли ли все карты меньше переданной. Вернет True - если все, что меньше, вышло, иначе - False """

        etalon = [i for i in range(6, card.value)]
        if not self._no_joker and card.lear == const.LEAR_SPADES and 7 in etalon:
            etalon.pop(etalon.index(7))

        return set(etalon) == set(
            (c.value for c in self._released_cards if c.lear == card.lear and c.value < card.value and not c.joker))

    def _ai_lear_released(self, lear, exclude_card=None):
        """ Смотрит по вышедшим все ли карты масти уже вышли (кроме указанной, если она передана). True - если да, иначе False """

        etalon = [i for i in range(6, 15) if exclude_card is None or exclude_card.value != i]
        if not self._no_joker and lear == const.LEAR_SPADES and 7 in etalon:
            etalon.pop(etalon.index(7))

        return set(etalon) == set((c.value for c in self._released_cards if c.lear == lear and (
            exclude_card is None or exclude_card.value != c.value) and not c.joker))

    def _ai_lear_over_safe(self, lear):
        """
        Смотрит по вышедшим мастям, по каждому игроку, кто еще не походил в этом круге (исключая текущего),
        что масть у пользователя уже закончилась вместе с козырем и т.о. по этому признаку
        на карту этой масти можно точно взять, если ходишь первый.
        True - если масти нет, козыря нет ни у кого, иначе False
        """

        ex_players = [ti[0] for i, ti in enumerate(self._order_table()) if i > self._step]
        ex_players.append(self._curr_player)

        for p in self._released_lears:
            if p not in ex_players:
                if lear in self._released_lears[p]:
                    if self._trump != const.LEAR_NOTHING and self._trump not in self._released_lears[p]:
                        return False
                else:
                    return False

        return True

    def _ai_lear_exists_or_over_safe(self, lear):
        """
        Смотрит по вышедшим мастям, по каждому игроку, кто еще не походил в этом круге (исключая текущего),
        что масть у пользователя или есть или закончилась вместе с козырем и т.о. по этому признаку на карту этой
        масти можно взять, если у тебя самая большая.
        True - если масть есть или масти нет и козыря нет по каждому, иначе False
        """

        ex_players = [ti[0] for i, ti in enumerate(self._order_table()) if i > self._step]
        ex_players.append(self._curr_player)

        for p in self._released_lears:
            if p not in ex_players:
                if lear in self._released_lears[p]:
                    if self._trump != const.LEAR_NOTHING and self._trump not in self._released_lears[p]:
                        return False

        return True

    def _ai_lear_or_trump_exists(self, lear):
        """
        Смотрит по вышедшим мастям, по каждому игроку, кто еще не походил в этом круге (исключая текущего),
        что у пользователя есть или масть или козырь и т.о. по этому признаку на карту этой
        масти можно скинуть, если у тебя самая маленькая.
        True - если масть есть или козырь есть по каждому, иначе False
        """

        ex_players = [ti[0] for i, ti in enumerate(self._order_table()) if i > self._step]
        ex_players.append(self._curr_player)

        for p in self._released_lears:
            if p not in ex_players:
                if lear in self._released_lears[p]:
                    if self._trump == const.LEAR_NOTHING or self._trump in self._released_lears[p]:
                        return False

        return True

    def _ai_card_covered(self, card, cards):
        """
        Оперделяет, прикрыта ли переданная карта.
        Карту считаем прикрытой, если есть все, что больше или есть столько меньших, сколько не хватает больших
        """

        # посчитаем кол-во пропущенных карт больше нашей
        x = 14 - card.value - len([c for c in cards if c.value > card.value])
        return len([c for c in cards if c.value < card.value]) >= x

    def _ai_is_cards_line(self, card, cards, start=14):
        """
        Выявляет сплошной ряд карт одной масти для переданной карты.
        Т.е. смотрит, есть ли непрерывная последовательность карт одной масти перед указанной картой,
        например Т К Д если передан В и т.п.
        start - карта, с которой должно быть начало ряда (т.е. ряд может начинаться не с Т)
        """

        return len([c for c in cards if c.value > card.value]) >= start - card.value

    def _ai_fill_order_cards(self, player, first_move):
        """
        Формирует набор карт игрока, на которые будет сделан заказ. Оболочка для разведения веток алгоритма по разным
        ситуациям: бескозырка / с козырями
        
        :param player: Игрок
        :param first_move: флаг, что этот игрок ходит первым
        """

        if self._trump == const.LEAR_NOTHING:
            self._ai_fill_order_no_trump(player, first_move)
        else:
            self._ai_fill_order_with_trump(player, first_move)

    def _ai_fill_order_no_trump(self, player, first_move):
        """ Формирует набор карт игрока, на которые будет сделан заказ при бескозырке """

        deal_cards = self._deals[self._curr_deal].cards
        max_cards = round(36 / self.party_size())
        rt = (round(max_cards / 3), round(max_cards / 2), round(max_cards / 1.3))[player.risk_level]
        rc = (4, 3, 2)[player.risk_level]
        no_see_cover = deal_cards < rt  # смотреть или нет прикрытость карты
        has_joker = player.card_exists(joker=True)
        joker_has_cover = has_joker

        for lear in range(4):
            has_other_ace = player.card_exists(value=14, exclude_lear=lear)
            cards = player.gen_lear_range(lear)

            # Вариант 1: сплошной ряд начиная с Т до первого разрыва
            series = [card for card in cards if self._ai_is_cards_line(card, cards)]
            if series:
                if len(series) == 9 or len(series) >= deal_cards - 1:
                    if has_joker or first_move:
                        # если полностью вся масть: заказать на нее можно только если есть дж или твой ход первый
                        player.add_to_order(series)
                    elif has_other_ace and flip_coin((1, 3, 5)[player.risk_level]):
                        # иначе если есть Т другой масти - можно рискнуть, но не на всю серию, т.к. ее могут выбрать
                        # раньше, чем дойдет ход
                        player.add_to_order(series[:round(len(series) / rc)])
                else:
                    if has_joker or first_move:
                        # если есть ДЖ или первый ход - можно смело заказывать
                        player.add_to_order(series)
                    else:
                        # а вот тут надо сделать выбор - рисковать или нет
                        # чем длиннее масть, тем меньше шансов, что кто-то кинет карту этой масти до того, как у тебя
                        # еще будет хватать карт, чтоб взять заказ, т.е. увеличиваем вероятность заказа с уменьшением
                        # длины масти так, чтоб Т К оставались со 100% вероятностью, а Д и далее в зависимости от
                        # уровня риска игрока
                        if len(series) <= 2:
                            player.add_to_order(series)
                        else:
                            if flip_coin(10 - len(series) - (2, 1, 0)[player.risk_level]):
                                for i, c in enumerate(series):
                                    if flip_coin(10 - i * 2):
                                        player.order_cards.append(c)
                                    else:
                                        break
            # Вариант 2: ряд начиная с К
            elif cards:
                if cards[0].value == 13 and (self._ai_card_covered(cards[0], cards) or
                                             (has_joker and joker_has_cover) or no_see_cover):
                    # если первая карта (К) прикрыта, тогда еще что-то можно попробовать.
                    # Заказываем только на короля, т.к. на остальное уже слишком опасно
                    player.order_cards.append(cards[0])
                    if has_joker and len(cards) == 1:
                        # прикрылись джокером - дальше им прикрываться нельзя будет
                        joker_has_cover = False

        if has_joker:
            # и закинем джокера, если он есть и еще не там
            j = player.cards[player.index_of_card(joker=True)]
            if j not in player.order_cards:
                player.order_cards.append(j)

    def _ai_fill_order_with_trump(self, player, first_move):
        """ Формирует набор карт игрока, на которые будет сделан заказ """

        deal_cards = self._deals[self._curr_deal].cards
        max_cards = round(36 / self.party_size())
        is_full = deal_cards == max_cards
        rt = (round(max_cards / 3), round(max_cards / 2), round(max_cards / 1.3))[player.risk_level]
        no_see_cover = deal_cards < rt  # смотреть или нет прикрытость карты
        trump_limit = 14 - (2, 3, 4)[player.risk_level]
        limit = 14 - player.risk_level
        has_joker = player.card_exists(joker=True)
        joker_has_cover = has_joker

        for lear in range(4):
            cards = player.gen_lear_range(lear)
            for card in cards:
                if lear == self._trump and self._trump != const.LEAR_NOTHING:
                    # если масть козырная - просто смотрим, что прикрыто и заказываем на все
                    covered = self._ai_card_covered(card, cards)
                    if is_full:
                        if covered or (has_joker and joker_has_cover) or len(cards) == 9:
                            player.order_cards.append(card)
                            if not covered:
                                joker_has_cover = False
                    else:
                        if no_see_cover:
                            if card.value > trump_limit:
                                player.order_cards.append(card)
                        elif covered:
                            player.order_cards.append(card)
                        elif has_joker and joker_has_cover:
                            player.order_cards.append(card)
                            joker_has_cover = False
                else:
                    # если не козырная, заказываем только на самые крупные - и то не всегда
                    covered = self._ai_card_covered(card, cards)
                    if is_full:
                        if (covered or (has_joker and joker_has_cover)) and card.value >= limit:
                            f = False
                            if len(cards) > (9 - self.party_size()):
                                if flip_coin((3, 4, 5)[player.risk_level]):
                                    player.order_cards.append(card)
                                    f = True
                            else:
                                player.order_cards.append(card)
                                f = True
                            if f and not covered:
                                joker_has_cover = False
                    else:
                        if card.value >= limit:
                            if no_see_cover:
                                if flip_coin((3, 4, 5)[player.risk_level]):
                                    player.order_cards.append(card)
                            elif covered:
                                player.order_cards.append(card)
                            elif has_joker and joker_has_cover:
                                player.order_cards.append(card)
                                joker_has_cover = False

        # если в заказе больше одногй некозырной карты меньше Т - может быть выкинем одну случайно выбранную для подстраховки
        kings = [(i, c.value) for i, c in enumerate(player.order_cards) if c.lear != self._trump and c.value <= 13]
        if len(kings) > 1 and flip_coin((6, 4, 2)[player.risk_level]):
            # если есть дамы - выберем из них
            queens = list(filter(lambda x: x[1] == 12, kings))
            if queens:
                player.order_cards.pop(queens[random.choice(range(len(queens)))])
            else:
                player.order_cards.pop(kings[random.choice(range(len(kings)))])

        if has_joker:
            # и закинем джокера, если он есть и еще не там
            j = player.cards[player.index_of_card(joker=True)]
            if j not in player.order_cards:
                player.order_cards.append(j)

    def _ai_calc_order(self):
        """
        Расчитывает заказ на текущий раунд. Возвращает кол-во взяток, которые предполагает взять и в темную делается заказ или нет.
        Заполняет у игрока массив карт, на которые рассчитывает взять. Возвращает int, bool (заказ, темная/нет)
        """

        player = self._players[self._curr_player]
        deal_type = self._deals[self._curr_deal].type_

        if deal_type == const.DEAL_BROW:
            # тут я вижу карты игроков, но не вижу свои, в раздаче всегда 1 карта
            is_dark = False
            b = True

            for p in self._players:
                if p != player:
                    if p.cards[0].joker and p.order == 1:
                        b = False
                    elif p.cards[0].lear == self._trump:
                        if p.cards[0].value >= 8 - const.RISK_BASE_COEFF[player.risk_level] * 2:
                            b = False
                    else:
                        if p.cards[0].value > 10 - const.RISK_BASE_COEFF[player.risk_level]:
                            b = False

                if not b: break

            if b:
                player.order_cards.append(player.cards[0])
        else:
            is_dark = deal_type == const.DEAL_DARK or (random.randint(0, 100) < 10 if self._dark_allowed else False)
            # формируем список карт, на которые рассчитываем взять в любом случае, они понадобятся потом в логике ИИ
            self._ai_fill_order_cards(player, self._deals[self._curr_deal].player == player)

        if is_dark:
            max_cnt = round(self._deals[self._curr_deal].cards / 3) - const.RISK_BASE_COEFF[player.risk_level]
            cnt = random.randint(0, max_cnt)

            # сбросим флаг, т.к. это не заказ в темную, а такая раздача - для игровой логики это имеет значение
            if deal_type == const.DEAL_DARK:
                is_dark = False
        else:
            cnt = len(player.order_cards)

        # проверка возможности сделать такой заказ и корректировка его, если нельзя: уменьшаем или увеличиваем
        # в зависимости от ситуации и уровня риска игрока до тех пор, пока не станет возможно
        start_cnt = cnt
        can, _ = self._check_order(cnt, is_dark)
        while not can:
            if cnt <= 0 or cnt >= len(player.cards):
                start_cnt = cnt

            if start_cnt <= 0:
                cnt += 1
            elif start_cnt >= len(player.cards):
                cnt -= 1
            else:
                cnt += (-1, random.choice((-1, 1)), 1)[player.risk_level]
                # cnt += random.choice((-1, 1))

            can, _ = self._check_order(cnt, is_dark)

        return cnt, is_dark

    def _ai_can_take(self, card):
        """ Вычисляет, возможно ли взять на карту. Пока True/False, но потом вполне возможно буду вероятность расчитывать """

        deal_cards = self._deals[self._curr_deal].cards
        max_cards = round(36 / self.party_size())
        no_full = deal_cards < max_cards

        if card.joker:
            return True

        # сразу разведем ветки анализа, когда раздаются все карты и не все
        if no_full:
            if self._ai_greater_cards_released(card) or self._ai_lear_over_safe(card.lear):
                return True
        else:
            if self._ai_greater_cards_released(card) and self._ai_lear_exists_or_over_safe(card.lear):
                return True

        return False

    def _ai_can_give(self, card, soft=False):
        """ Вычисляет, возможно ли сбросить карту. Пока True/False, но потом вполне возможно буду вероятность расчитывать """

        deal_cards = self._deals[self._curr_deal].cards
        max_cards = round(36 / self.party_size())
        no_full = deal_cards < max_cards

        if card.joker:
            return False

        # сразу разведем ветки анализа, когда раздаются все карты и не все
        if no_full:
            if soft:
                if card.value < 6 + self.party_size() - 1 and self._ai_lear_or_trump_exists(card.lear):
                    return True
            else:
                if self._ai_smallest_cards_released(card) and self._ai_lear_or_trump_exists(card.lear):
                    return True
        else:
            if self._ai_smallest_cards_released(card) and self._ai_lear_or_trump_exists(card.lear):
                return True

        return False

    def _ai_calc_walk(self) -> int:
        """
        Вычисляет, чем походить. Для случаев, когда ходишь первый. Возвращает индекс карты в массиве карт игрока.
        Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        player = self._players[self._curr_player]
        deal_type = self._deals[self._curr_deal].type_
        deal_cards = self._deals[self._curr_deal].cards
        max_cards = round(36 / self.party_size())
        no_full = deal_cards < max_cards
        limit = (round(max_cards / 3), round(max_cards / 2), round(max_cards / 1.3))[player.risk_level]
        card = None

        if deal_type == const.DEAL_GOLD or (
            deal_type not in (const.DEAL_GOLD, const.DEAL_MIZER) and player.order != player.take):
            # или еще не набрал или уже перебрал - надо брать

            for step in (1, 2):
                # 1 круг
                # смотрим в случайном порядке в тех, на которые заказали, можно ли картой уже ходить (т.е. все, что больше, вышло)
                # 2 круг
                # если ничего не нашли из заказанного - повторим процедуру со всеми остальными картами, но в порядке убывания величины
                if step == 1:
                    cards = [c for c in player.cards_sorted() if c in player.order_cards]
                    random.shuffle(cards)
                else:
                    cards = [c for c in player.cards_sorted()]

                for c in cards:
                    if self._ai_can_take(c) and (not c.joker or step == 2):
                        card = c
                        break

                # если уже срочно пора брать, иначе просто не хватит карт, чтоб набрать - ходим джокером
                if not card:
                    if deal_type != const.DEAL_GOLD and (player.order - player.take) >= len(player.cards):
                        n = player.index_of_card(joker=True)
                        if n > -1:
                            card = player.cards[n]
                            # выберем для джокера действие и масть. Зависит от того, прикрывали мы им что-то или нет.
                            # Прикрыть на заказе им мы могли только короля, так что поищем. Сначала козырного, потом простых
                            # т.к. до этого мы уже перебрали все, на что рассчитывали - тут можно уже не проверять, вышла ли угрожающая
                            cnt = [c for c in player.order_cards if c.value == 13 and c.lear != self._trump]
                            if self._trump != const.LEAR_NOTHING:
                                ct = [c for c in player.order_cards if c.value == 13 and c.lear == self._trump]
                                if ct:
                                    card.joker_action = const.JOKER_TAKE_BY_MAX
                                    card.joker_lear = ct[0].lear
                            if card.joker_action is None:
                                if cnt:
                                    card.joker_action = const.JOKER_TAKE_BY_MAX
                                    card.joker_lear = cnt[random.randrange(0, len(cnt))].lear

                # ничего не нашли - нужно кинуть что-то для затравки, чтобы вынудить сбросить мешающую крупную -
                # подберем что-то не самое мелкое той же масти, как карты из списка заказа
                if not card:
                    for co in player.order_cards:
                        c = player.middle_card(co.lear)
                        if c:
                            cl = player.gen_lear_range(co.lear)
                            i = cl.index(c)

                            while i < len(cl) and (cl[i].value >= co.value or cl[i] in player.order_cards):
                                i += 1

                            if i < len(cl):
                                card = cl[i]
                                break
                else:
                    break

            # полезного ничего вычислить не получилось (напрмер потому, что розданы не все карты) -
            # просто берем самую большую по номиналу для неполной раздачи или самую мелкую при полной
            if not card:
                if no_full and deal_cards <= limit:
                    card = [c for c in player.cards_sorted()][0]
                else:
                    card = [c for c in player.cards_sorted(ascending=True)][0]

            # если выбран джокер:
            if card.joker:
                # если мы на золотой - можно поискать среди карт неприкрытую крупную и прикрыть ее
                if deal_type == const.DEAL_GOLD:
                    cnt = [c for c in player.cards if c.value == 13 and c.lear != self._trump]
                    if self._trump != const.LEAR_NOTHING:
                        ct = [c for c in player.cards if c.value == 13 and c.lear == self._trump]
                        if ct:
                            card.joker_action = const.JOKER_TAKE_BY_MAX
                            card.joker_lear = ct[0].lear
                    if card.joker_action is None:
                        if cnt:
                            card.joker_action = const.JOKER_TAKE_BY_MAX
                            card.joker_lear = cnt[random.randrange(0, len(cnt))].lear

                # тут масть и "по самой большой" уже от фонаря - эти вещи если выбраны, то раньше
                if card.joker_action is None:
                    card.joker_action = const.JOKER_TAKE_BY_MAX \
                        if self._joker_demand_peak and flip_coin(3) else const.JOKER_TAKE
                if card.joker_lear is None:
                    card.joker_lear = self._trump if self._trump != const.LEAR_NOTHING else random.randint(0, 3)
        else:
            # взято свое - надо скинуть - ходим самой мелкой, сразу проверим, что масть этой карты еще не вышла
            # и что не вышли карты крупнее ее (насколько это возможно), чтоб не облажатся
            cards = [c for c in player.cards_sorted(ascending=True)]
            for c in cards:
                if self._ai_can_give(c):
                    card = c
                    break

            # посмотрим тогда так - помягче условие
            if not card:
                for c in cards:
                    if self._ai_can_give(c, soft=True):
                        card = c
                        break

            # ничего не нашли - просто берем самую маленькую
            if not card:
                card = cards[0]

            # а вот тут проверим - может стоит джокера кинуть
            if self._ai_lear_over_safe(card.lear):
                idx = player.index_of_card(joker=True)
                if idx > -1:
                    card = player.cards[idx]

            if card.joker:
                card.joker_action = const.JOKER_GIVE
                card.joker_lear = card.lear if self._joker_give_at_par else random.choice(
                    [i for i in range(4) if i != self._trump and not self._ai_lear_released(i)])
                if card.joker_lear is None:
                    card.joker_lear = random.choice([i for i in range(4) if i != self._trump])

        return player.cards.index(card)

    def _ai_calc_beat(self) -> int:
        """
        Вычисляет, чем покрыть карты на столе. Для случаев, когда ходишь НЕ первый. Возвращает индекс карты в массиве карт игрока.
        Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        player = self._players[self._curr_player]
        tbl_ordered = self._order_table()
        deal_type = self._deals[self._curr_deal].type_
        walk_lear = tbl_ordered[0][1].card.lear if not tbl_ordered[0][1].is_joker() else tbl_ordered[0][1].joker_lear()

        if deal_type == const.DEAL_GOLD or (
            deal_type not in (const.DEAL_GOLD, const.DEAL_MIZER) and player.order != player.take):
            # или еще не набрал или уже перебрал - надо брать
            # Берем самую большую заданной масти
            c = player.max_card(walk_lear)

            if not c:
                # если масти нет - берем самый большой козырь
                c = player.max_card(self._trump)
            elif tbl_ordered[0][1].is_joker() and tbl_ordered[0][1].joker_action() == const.JOKER_TAKE_BY_MAX:
                # если есть и заказывали по старшей - придется вернуть ее
                pass
            else:
                # если самая большая моя не бьет то, что уже на столе или
                # мой ход не последний и что-то не вышло, что может побить это карту - ищем дальше...
                take = c == self._ai_max_card(*(ti[1].card for ti in tbl_ordered), c)

                if len(self._table) < self.party_size() - 1:
                    # если я хожу не последний - проверить, что вышло все, что больше, и что не вышла масть или вышла с козырем
                    take = take and self._ai_can_take(c)

                if not take:
                    c = player.min_card(walk_lear)

                    # посмотрим - не просираем ли мы карту, на которую рассчитывали
                    if c in player.order_cards:
                        n = player.index_of_card(joker=True)
                        if n > -1:
                            c = player.cards[n]

            # масти нет, козыря нет - придется скидывать - надо выбрать что-то ненужное
            if not c:
                # если уже срочно пора брать, иначе просто не хватит карт, чтоб набрать
                if deal_type == const.DEAL_GOLD or (player.order - player.take) >= len(player.cards):
                    n = player.index_of_card(joker=True)
                    if n > -1:
                        c = player.cards[n]

                cards = [c for c in player.cards_sorted(ascending=True) if c not in player.order_cards]
                if not cards:
                    cards = [c for c in player.cards_sorted(ascending=True)]

                if not c:
                    c = cards[0]

            if c.joker:
                c.joker_action = const.JOKER_TAKE
                c.joker_lear = self._trump if self._trump != const.LEAR_NOTHING else walk_lear
        else:
            # свое взято - надо сливать - слить надо самую крупную из возможных
            c = None

            if tbl_ordered[0][1].is_joker() and tbl_ordered[0][1].joker_action() == const.JOKER_TAKE_BY_MAX:
                # если требовали по старшей - придется вернуть старшую. Ищем ее
                c = player.max_card(walk_lear)
            else:
                # иначе находим самую большую из тех, на которую точно не возьмешь
                # и точно такая же логика для козыря
                for lear in (walk_lear, self._trump):
                    if lear == const.LEAR_NOTHING:
                        continue

                    take = False

                    for c in player.gen_lear_range(lear):
                        take = c == self._ai_max_card(*(ti[1].card for ti in tbl_ordered), c)
                        if not take:
                            if len(tbl_ordered) < self.party_size() - 1:
                                take = self._ai_can_take(c)  # not self._ai_can_give(c)
                            if not take:
                                break

                    # если всетаки бьем - найденная будет самой маленькой картой этой масти из моих
                    # если походили все, кроме меня: на мизере берем самую большую, в остальных - так и оставляем,
                    # потому что если не мизер - то дальше наша стратегия - набрать как можно больше.
                    # если походили не все - оставляем маленькую - это шанс, что у кого-то есть больше
                    # (потом будет еще анализ вышедших)
                    if take:
                        if len(tbl_ordered) == self.party_size() - 1:
                            if deal_type == const.DEAL_MIZER:
                                c = player.max_card(lear)

                    if c:
                        break

                # а теперь посмотрим - если есть серьезный шанс взять - кинем джокера (если он есть конечно)
                if take:
                    n = player.index_of_card(joker=True)
                    if n > -1:
                        c = player.cards[n]

            # нет ни масти ни козыря (и джокер не понадобился)
            if not c:
                # выкинуть самую большую из имеющихся
                c = [c for c in player.cards_sorted()][0]

            if c.joker:
                c.joker_action = const.JOKER_GIVE
                c.joker_lear = c.lear if self._joker_give_at_par else walk_lear

        return player.cards.index(c)
