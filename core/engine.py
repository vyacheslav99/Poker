""" Реализация механизмов ИИ на базе игрового движка. ИИ обычного уровня """

import random

from core import const, base
from core.helpers import flip_coin


class Engine(base.BaseEngine):

    def __init__(self, players: list, **options):
        super(Engine, self).__init__(players, **options)

    # --==** Реализация движка ИИ **==--

    def _ai_fix_released_card(self, card):
        """
        Сбор и анализ данных по ходам игроков
        Результаты будут использованы в алгоритмах ИИ
        """

        super(Engine, self)._ai_fix_released_card(card)

        if self._curr_player is not None:
            # 1. посмотрим по вышедшим картам - если все карты масти вышли - запишем всем игрокам
            # в вышедшие масти эту масть
            if not card.joker:
                all_cards = [i for i in range(6, 15)]
                if not self._no_joker and card.lear == const.LEAR_SPADES and 7 in all_cards:
                    all_cards.pop(all_cards.index(7))

                released = [c.value for c in self._released_cards if c.lear == card.lear and not c.joker]

                if set(all_cards) == set(released):
                    for p in range(self.party_size()):
                        self._released_lears[p].add(card.lear)

            # 2. определим, закончилась ли у игрока масть, которой заходили, и если да, то запишем игроку
            # в вышедшие масти; заодно можно вычислить, закончился ли козырь
            if self._step > 0 and not card.joker:
                _, tbl_item = self._order_table()[0]
                tbl_lear = tbl_item.card.lear if not tbl_item.card.joker else tbl_item.card.joker_lear

                if card.lear != tbl_lear:
                    # если походил не в масть - эта масть у него закончилась
                    self._released_lears[self._curr_player].add(tbl_lear)

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

    def _ai_greater_cards_count(self, card):
        """ Подсчитывает по вышедшим, сколько осталось карт крупнее переданной и возвращает это число """

        ex_cards = self._players[self._curr_player].gen_lear_range(card.lear)
        return len([c for c in self._released_cards
                    if c.lear == card.lear and c.value > card.value and not c.joker and c not in ex_cards])

    def _ai_greater_cards_released(self, card):
        """
        Смотрит по вышедшим, вышли ли все карты крупнее переданной.
        Вернет True - если все, что больше, вышло, иначе - False
        """

        ex_cards = [c.value for c in self._players[self._curr_player].gen_lear_range(card.lear)]
        etalon = [i for i in range(card.value + 1, 15) if i not in ex_cards]
        if not self._no_joker and card.lear == const.LEAR_SPADES and 7 in etalon:
            etalon.pop(etalon.index(7))

        return set(etalon) == set(
            (c.value for c in self._released_cards if c.lear == card.lear and c.value > card.value and not c.joker))

    def _ai_smallest_cards_released(self, card):
        """
        Смотрит по вышедшим, вышли ли все карты меньше переданной.
        Вернет True - если все, что меньше, вышло, иначе - False
        """

        ex_cards = [c.value for c in self._players[self._curr_player].gen_lear_range(card.lear)]
        etalon = [i for i in range(6, card.value) if i not in ex_cards]
        if not self._no_joker and card.lear == const.LEAR_SPADES and 7 in etalon:
            etalon.pop(etalon.index(7))

        return set(etalon) == set(
            (c.value for c in self._released_cards if c.lear == card.lear and c.value < card.value and not c.joker))

    def _ai_lear_released(self, lear):
        """ Смотрит по вышедшим все ли карты масти уже вышли """

        ex_cards = [c.value for c in self._players[self._curr_player].gen_lear_range(lear)]
        etalon = [i for i in range(6, 15) if i not in ex_cards]
        if not self._no_joker and lear == const.LEAR_SPADES and 7 in etalon:
            etalon.pop(etalon.index(7))

        return set(etalon) == set((c.value for c in self._released_cards if c.lear == lear and not c.joker))

    def _ai_lear_over_safe(self, lear, oper=True):
        """
        Смотрит по вышедшим мастям, по каждому игроку, что масть у пользователя уже закончилась вместе с козырем и
        т.о. по этому признаку на карту этой масти можно точно взять, если ходишь первый.
        Игроков просматиривает или по оперативной ситуации на столе (oper=True) - т.е. только тех, кто еще не ходил;
        или всех (oper=False).
        True - если масти нет, козыря нет НИ У КОГО, иначе False
        """

        if oper:
            ex_players = [ti[0] for ti in self._order_table()]
        else:
            ex_players = []

        ex_players.append(self._curr_player)

        for p in self._released_lears:
            if p not in ex_players:
                if lear in self._released_lears[p]:
                    if self._trump != const.LEAR_NOTHING and self._trump not in self._released_lears[p]:
                        return False
                else:
                    return False

        return True

    def _ai_lear_exists_or_over_safe(self, lear, oper=True):
        """
        Смотрит по вышедшим мастям, по каждому игроку, что масть у пользователя или есть или закончилась
        вместе с козырем и т.о. по этому признаку на карту этой масти можно взять, если у тебя самая большая.
        Игроков просматиривает или по оперативной ситуации на столе (oper=True) - т.е. только тех, кто еще не ходил;
        или всех (oper=False).
        True - если масть есть или масти нет и козыря нет У ВСЕХ ИГРОКОВ, иначе False
        """

        if oper:
            ex_players = [ti[0] for ti in self._order_table()]
        else:
            ex_players = []

        ex_players.append(self._curr_player)

        for p in self._released_lears:
            if p not in ex_players:
                if lear in self._released_lears[p]:
                    if self._trump != const.LEAR_NOTHING and self._trump not in self._released_lears[p]:
                        return False

        return True

    def _ai_lear_or_trump_exists(self, lear, oper=True):
        """
        Смотрит по вышедшим мастям, по каждому игроку, что у пользователя есть или масть или козырь и т.о.
        по этому признаку на карту этой масти можно скинуть, если у тебя самая маленькая.
        Игроков просматиривает или по оперативной ситуации на столе (oper=True) - т.е. только тех, кто еще не ходил;
        или всех (oper=False).
        True - если масть или козырь ЕСТЬ ХОТЯ БЫ У ОДНОГО из игроков, иначе False
        """

        if oper:
            ex_players = [ti[0] for ti in self._order_table()]
        else:
            ex_players = []

        ex_players.append(self._curr_player)

        for p in self._released_lears:
            if p not in ex_players:
                if lear in self._released_lears[p]:
                    if self._trump != const.LEAR_NOTHING and self._trump not in self._released_lears[p]:
                        return True
                else:
                    return True

        return False

    def _ai_card_covered(self, card, cards):
        """
        Оперделяет, прикрыта ли переданная карта.
        Карту считаем прикрытой, если карт меньше нашей столько, сколько от нашей до Т (включительно), за вычитом тех
        более крупных, что есть у нас на руках (т.к. от них прикрываться не надо).
        Вернет bool: прикрыта/нет
        """

        return len([c for c in cards if c.value != card.value and not c.joker]) >= 14 - card.value

    def _ai_card_covered_wj(self, card, cards, has_joker=False):
        """
        Оперделяет, прикрыта ли переданная карта, с учетом джокера.
        Карту считаем прикрытой, если карт меньше нашей (+ Дж, если передан флаг) столько, сколько от нашей
        до Т (включительно), за вычитом тех более крупных, что есть у нас на руках (т.к. от них прикрываться не надо).
        Если has_joker True - то учесть джокера (подразумевается, что он есть), как еще одну из прикрывающих карт.
        Вернет bool, bool: прикрыта/нет, использован джокер/нет
        """

        cover_cnt = len([c for c in cards if c.value != card.value and not c.joker])

        if cover_cnt >= 14 - card.value:
            return True, False

        if has_joker and cover_cnt + 1 >= card.value:
            return True, True
        else:
            return False, False

    def _ai_is_cards_line(self, card, cards, start=14):
        """
        Выявляет сплошной ряд карт одной масти для переданной карты.
        Т.е. смотрит, есть ли непрерывная последовательность карт одной масти перед указанной картой,
        например Т К Д если передан В и т.п.
        start - карта, с которой должно быть начало ряда (т.е. ряд может начинаться не с Т)
        """

        return len([c for c in cards if c.value > card.value]) >= start - card.value

    def _ai_select_joker_lear_to_shield(self, cards):
        """
        Выбирает масть для захода джокером (твой ход первый) чтобы забрать и при этом прикрыть другую карту.
        Подбирает наиболее перспективную карту для прикрытия.

        :param cards: Упорядоченный в порядке приоритета набор карт, среди которых надо выбрать
        :return: Найденную масть. Если не выбрал подходящую, вернет None
        """

        # сначала смотрим по козырям
        if self._trump != const.LEAR_NOTHING:
            # составим список неприкрытых карт
            cand = [c for c in cards if c.lear == self._trump and not self._ai_card_covered(c, cards)]
            if cand and self._ai_greater_cards_count(cand[0]) - 1 <= 0:
                return cand[0].lear

        # не нашли, посомтрим среди простых
        # составим список крупных неприкрытых карт
        cand = [c for c in cards if c.value > 11 and c.lear != self._trump
                and not self._ai_card_covered(c, cards)]
        if cand:
            for c in cand:
                # простую масть выбираем с подстраховкой, а то можно просрать джокера на козыре
                if self._ai_lear_exists_or_over_safe(c.lear) and self._ai_greater_cards_count(c) - 1 <= 0:
                    return c.lear

        # подходящую не нашли - или 1 джокера недостаточно, чтоб прикрыть, или прикрывать нечего
        return None

    def _ai_player_take_state(self, player):
        """ Возвращает состояние игрока по взяткам на данный момент """

        deal_type = self._deals[self._curr_deal].type_

        if deal_type == const.DEAL_GOLD:
            return const.TAKE_STATE_POOR
        elif deal_type == const.DEAL_MIZER:
            return const.TAKE_STATE_OVERDO
        else:
            if player.take < player.order:
                return const.TAKE_STATE_POOR
            elif player.take > player.order:
                return const.TAKE_STATE_OVERDO
            else:
                return const.TAKE_STATE_OK

    def _ai_player_take_over(self, player):
        """ Перебрал игрок или нет """

        return self._ai_player_take_state(player) == const.TAKE_STATE_OVERDO

    def _ai_player_take_poor(self, player):
        """ Недобрал игрок или нет """

        return self._ai_player_take_state(player) == const.TAKE_STATE_POOR

    def _ai_player_take_ok(self, player):
        """ Взял свое игрок или нет """

        return self._ai_player_take_state(player) == const.TAKE_STATE_OK

    def _ai_fill_order_cards(self, player, first_move):
        """
        Формирует набор карт игрока, на которые будет сделан заказ. Оболочка для разведения веток алгоритма по разным
        ситуациям: бескозырка / с козырями
        
        :param player: Игрок
        :param first_move: флаг, что этот игрок ходит первым
        :return: карта, на которую можно сделать доп. заказ, если нельзя сделать рассчитанный
        """

        if self._trump == const.LEAR_NOTHING:
            return self._ai_fill_order_no_trump(player, first_move)
        else:
            return self._ai_fill_order_with_trump(player, first_move)

    def _ai_fill_order_no_trump(self, player, first_move):
        """ Формирует набор карт игрока, на которые будет сделан заказ при бескозырке """

        grow_card = None
        deal_cards = self._deals[self._curr_deal].cards
        # max_cards = round(36 / self.party_size())

        if self.party_size() > 3:
            ck = (3, 4, 5)[player.risk_level]
            rc = (4, 3, 2)[player.risk_level]
        else:
            ck = (4, 5, 6)[player.risk_level]
            rc = (3, 2, 1.5)[player.risk_level]
        no_see_cover = deal_cards < ck  # смотреть или нет прикрытость карты
        lim = 14 - (2 + player.risk_level)
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
                        grow_card = series[round(len(series) / rc) - 1]
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
                                        grow_card = c
                                        break
            # Вариант 2: ряд начинается с меньшей, чем Т
            elif cards:
                if self.party_size() > 3:
                    # Если больше 3-х игроков, то так
                    covered, joker_used = self._ai_card_covered_wj(cards[0], cards, joker_has_cover)
                    if cards[0].value == 13 and (covered or no_see_cover):
                        # если первая карта (К) прикрыта, тогда еще что-то можно попробовать.
                        # Заказываем только на короля, т.к. на остальное уже слишком опасно
                        player.order_cards.append(cards[0])
                        if joker_used:
                            # прикрылись джокером - дальше им прикрываться нельзя будет
                            joker_has_cover = False
                else:
                    # При трех игроках логика иная: если есть крупные другой масти (или джокер), то будем заказывать -
                    # просто смотрим, прикрыта ли карта и заказываем на нее, до определенного порога, зависящего от
                    # уровня риска игрока (порог нужен, чтоб было что скинуть, если вдруг ход не успеет дойти вовремя)
                    if has_joker or has_other_ace:
                        for i, c in enumerate(cards):
                            covered, joker_used = self._ai_card_covered_wj(c, cards, joker_has_cover)
                            if covered or (no_see_cover and c.value > lim):
                                player.order_cards.append(c)
                                if covered and joker_used:
                                    joker_has_cover = False
                            else:
                                break

        if has_joker:
            # и закинем джокера, если он есть и еще не там
            j = player.cards[player.index_of_card(joker=True)]
            if j not in player.order_cards:
                player.order_cards.append(j)

        return grow_card

    def _ai_fill_order_with_trump(self, player, first_move):
        """ Формирует набор карт игрока, на которые будет сделан заказ """

        grow_card = None
        deal_cards = self._deals[self._curr_deal].cards
        max_cards = round(36 / self.party_size())
        is_full = deal_cards == max_cards
        if self.party_size() > 3:
            ck = (3, 4, 5)[player.risk_level]
            trump_limit = 14 - (2, 3, 4)[player.risk_level]
            limit = 14 - player.risk_level
            x_factor = (3, 4, 5)[player.risk_level]
        else:
            ck = (4, 5, 6)[player.risk_level]
            trump_limit = 14 - (3, 4, 5)[player.risk_level]
            limit = 14 - (1 + player.risk_level)
            x_factor = (5, 6, 7)[player.risk_level]
        no_see_cover = deal_cards < ck  # смотреть или нет прикрытость карты
        has_joker = player.card_exists(joker=True)
        joker_has_cover = has_joker

        for lear in range(4):
            cards = player.gen_lear_range(lear)
            for card in cards:
                if lear == self._trump and self._trump != const.LEAR_NOTHING:
                    # если масть козырная - просто смотрим, что прикрыто и заказываем на все
                    covered, joker_used = self._ai_card_covered_wj(card, cards, joker_has_cover)
                    if is_full:
                        if covered or len(cards) == 9:
                            player.order_cards.append(card)
                            if covered and joker_used:
                                joker_has_cover = False
                    else:
                        if covered:
                            player.order_cards.append(card)
                            if joker_used:
                                joker_has_cover = False
                        elif no_see_cover:
                            if card.value > trump_limit:
                                player.order_cards.append(card)
                else:
                    # если не козырная, заказываем только на самые крупные - и то не всегда
                    covered, joker_used = self._ai_card_covered_wj(card, cards, joker_has_cover)
                    if is_full:
                        if covered and card.value >= limit:
                            f = False
                            if len(cards) > (9 - self.party_size()):
                                if flip_coin(x_factor):
                                    player.order_cards.append(card)
                                    f = True
                            else:
                                player.order_cards.append(card)
                                f = True
                            if f and joker_used:
                                joker_has_cover = False
                    else:
                        if card.value >= limit:
                            if covered:
                                player.order_cards.append(card)
                                if joker_used:
                                    joker_has_cover = False
                            elif no_see_cover:
                                if flip_coin(x_factor - (14 - card.value)):
                                    player.order_cards.append(card)

        if self.party_size() > 3:
            k = 13
        else:
            k = 12

        # если в заказе больше одной некозырной карты меньше Т - может быть выкинем одну случайно выбранную для подстраховки
        kings = [(i, c.value) for i, c in enumerate(player.order_cards) if c.lear != self._trump and c.value <= k]
        if len(kings) > 1 and flip_coin((6, 4, 2)[player.risk_level]):
            # если есть дамы - выберем из них
            # если мы что-то выкинули, запомним это - пригодиться, если будет нельзя сделать рассчитанный заказ
            queens = list(filter(lambda x: x[1] <= k - 1, kings))
            if queens:
                grow_card = player.order_cards.pop(queens[random.choice(range(len(queens)))][0])
            else:
                grow_card = player.order_cards.pop(kings[random.choice(range(len(kings)))][0])

        if has_joker:
            # и закинем джокера, если он есть и еще не там
            j = player.cards[player.index_of_card(joker=True)]
            if j not in player.order_cards:
                player.order_cards.append(j)

        return grow_card

    def _ai_fill_order_to_gold(self, player):
        """ Формирует набор карт игрока, на которые потенциально можно взять. Для золотой """

        has_joker = player.card_exists(joker=True)
        joker_has_cover = has_joker

        for lear in sorted([i for i, l in enumerate(const.LEAR_NAMES)], key=lambda x: x == self._trump, reverse=True):
            cards = player.gen_lear_range(lear)
            for card in cards:
                # просто закидываем все, что прикрыто
                covered, joker_used = self._ai_card_covered_wj(card, cards, joker_has_cover)
                if covered:
                    player.order_cards.append(card)
                    if joker_used:
                        joker_has_cover = False

    def _ai_calc_order(self):
        """
        Расчитывает заказ на текущий раунд. Возвращает кол-во взяток, которые предполагает взять и
        в темную делается заказ или нет.
        Заполняет у игрока массив карт, на которые рассчитывает взять. Возвращает int, bool (заказ, темная/нет)
        """

        player = self._players[self._curr_player]
        deal_type = self._deals[self._curr_deal].type_
        gc = None

        if deal_type == const.DEAL_BROW:
            # тут я вижу карты игроков, но не вижу свои, в раздаче всегда 1 карта
            is_dark = False
            b = True

            for p in self._players:
                if p != player:
                    if p.cards[0].joker and p.order in (-1, 1):
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
            gc = self._ai_fill_order_cards(player, self._deals[self._curr_deal].player == player)

        if is_dark:
            if self.party_size() > 3:
                max_cnt = round(self._deals[self._curr_deal].cards / 3) - const.RISK_BASE_COEFF[player.risk_level]
            else:
                max_cnt = round(self._deals[self._curr_deal].cards / 2) - 1 - const.RISK_BASE_COEFF[player.risk_level]
            if max_cnt < 1:
                max_cnt = self._deals[self._curr_deal].cards

            min_cnt = 0 if flip_coin(10, 100) else 1
            cnt = random.randint(min_cnt, max_cnt)

            # сбросим флаг, т.к. это не заказ в темную, а такая раздача - для игровой логики это имеет значение
            if deal_type == const.DEAL_DARK:
                is_dark = False
        else:
            cnt = len(player.order_cards)

        # проверка возможности сделать такой заказ и корректировка его, если нельзя: уменьшаем или увеличиваем
        # в зависимости от ситуации и уровня риска игрока до тех пор, пока не станет возможно
        start_cnt = cnt
        can, _ = self.check_order(cnt, is_dark)
        while not can:
            if cnt <= 0 or cnt >= len(player.cards):
                start_cnt = cnt

            if start_cnt <= 0:
                cnt += 1
                if gc:
                    player.order_cards.append(gc)
            elif start_cnt >= len(player.cards):
                cnt -= 1
            else:
                if gc:
                    cnt += (-1, random.choice((-1, 1)), 1)[player.risk_level]
                    player.order_cards.append(gc)
                else:
                    cnt -= 1

            can, _ = self.check_order(cnt, is_dark)

        return cnt, is_dark

    def _ai_can_take(self, card, oper=True):
        """
        Вычисляет, возможно ли взять на карту.
        Смотрит игроков или по оперативному анализу ситуации на столе (только еще не походивших в этом круге игроков)
        или всех
        """

        deal_cards = self._deals[self._curr_deal].cards
        max_cards = round(36 / self.party_size())
        no_full = deal_cards < max_cards

        if card.joker:
            return True

        # сразу разведем ветки анализа, когда раздаются все карты и не все
        if no_full:
            # вышли все крупнее этой карты или у всех, кто после закончилась масть и козырь
            if self._ai_greater_cards_released(card) or self._ai_lear_over_safe(card.lear, oper):
                return True
        else:
            # вышли все крупнее этой карты и у всех, кто после масть или есть или нет и нет козыря
            if self._ai_greater_cards_released(card) and self._ai_lear_exists_or_over_safe(card.lear, oper):
                return True

        return False

    def _ai_can_give(self, card, soft=False):
        """ Вычисляет, возможно ли сбросить карту. По оперативному анализу ситуации на столе и еще непоходивших игроков """

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

    def _ai_calc_walk_gold(self) -> int:
        """
        Вычисляет, чем походить при золотой. Для случаев, когда ходишь первый.
        Возвращает индекс карты в массиве карт игрока. Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        player = self._players[self._curr_player]
        card = None

        # предварительно заполним набор тех карт, на которые потенциально можно взять
        if not player.order_cards:
            self._ai_fill_order_to_gold(player)

        # однозначно - всегда надо брать!
        # составим список карт: сначала те, на которые рсчет, потом остальные по убыванию
        cards = [c for c in player.cards_sorted() if c in player.order_cards] + \
                [c for c in player.cards_sorted() if c not in player.order_cards]

        # ищем карту, на которую можно гарантированно взять
        for c in cards:
            if self._ai_can_take(c) and not c.joker:
                card = c
                break

        # гарантированно берущей нет; можно поискать среди карт неприкрытую крупную и прикрыть ее джокером
        if not card:
            n = player.index_of_card(joker=True)
            if n > -1:
                l = self._ai_select_joker_lear_to_shield(cards)
                # есть что прикрыть - выбираем джокера, иначе ждем до более благоприятного момента
                if l is not None and self._joker_demand_peak:
                    card = player.cards[n]
                    card.joker_action = const.JOKER_TAKE_BY_MAX
                    card.joker_lear = l

        # ничего не нашли - нужно кинуть что-то для затравки, чтобы вынудить сбросить мешающую крупную;
        # выбираем самую мелкую той же масти, как что-то из того, на что возможно взять
        if not card:
            for co in [c for c in cards if c in player.order_cards]:
                c = player.min_card(co.lear)
                if c and c != co:
                    card = c
                    break

        # ничего полезного не нашлось - просто берем случайно выбранную из самых мелких
        if not card:
            cards = [c for c in player.cards_sorted(ascending=True) if not c.joker]

            if cards:
                card = cards[0]
            else:
                # это значит остался только джокер - просто забираем
                card = player.cards[0]
                card.joker_action = const.JOKER_TAKE
                card.joker_lear = self._trump if self._trump != const.LEAR_NOTHING else random.choice(
                    [l for l in range(len(const.LEAR_NAMES))])

        return player.cards.index(card)

    def _ai_calc_walk(self) -> int:
        """
        Вычисляет, чем походить. Для случаев, когда ходишь первый. Возвращает индекс карты в массиве карт игрока.
        Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        deal_type = self._deals[self._curr_deal].type_

        if deal_type == const.DEAL_GOLD:
            return self._ai_calc_walk_gold()

        player = self._players[self._curr_player]
        deal_cards = self._deals[self._curr_deal].cards
        max_cards = round(36 / self.party_size())
        no_full = deal_cards < max_cards
        limit = (round(max_cards / 3), round(max_cards / 2), round(max_cards / 1.3))[player.risk_level]
        card = None

        if deal_type != const.DEAL_MIZER and player.order != player.take:
            # или еще не набрал или уже перебрал - надо брать
            # составим список карт: сначала те, на которые рссчет, потом остальные по убыванию
            cards = [c for c in player.cards_sorted() if c in player.order_cards] + \
                    [c for c in player.cards_sorted() if c not in player.order_cards]

            # ищем карту, на которую можно гарантированно взять
            for c in cards:
                if self._ai_can_take(c) and not c.joker:
                    card = c
                    break

            # надежно берущей нет; если уже срочно пора брать, иначе просто не хватит карт, чтоб набрать - ходим джокером
            if not card:
                if (player.order - player.take) >= len(player.cards):
                    n = player.index_of_card(joker=True)
                    if n > -1:
                        card = player.cards[n]
                        card.joker_action = const.JOKER_TAKE_BY_MAX if self._joker_demand_peak else const.JOKER_TAKE
                        # выберем для джокера масть - подберем масть так, чтоб прикрыть какую-то из карт,
                        # которую есть необходимость и возможность прикрыть джокером
                        card.joker_lear = self._ai_select_joker_lear_to_shield(cards)

                        if card.joker_lear is None:
                            # прикрывать нечего, а забирать надо без вариантов - просто забираем самый крупный козырь
                            # или случайно выбранную масть из имеющихся у игрока на бескозырке
                            card.joker_lear = self._trump if self._trump != const.LEAR_NOTHING else random.choice(
                                list(set([c.lear for c in player.cards])))

            # ничего не нашли - нужно кинуть что-то для затравки, чтобы вынудить сбросить мешающую крупную;
            # подберем что-то не самое мелкое той же масти, как то, на что возможно взять
            if not card:
                for co in cards:
                    c = player.middle_card(co.lear)
                    if c:
                        cl = player.gen_lear_range(co.lear)
                        i = cl.index(c)

                        while i < len(cl) and (cl[i].value >= co.value or cl[i] in player.order_cards):
                            i += 1

                        if i < len(cl):
                            card = cl[i]
                            break

            # все еще ничего не подобрали
            # просто берем самую большую по номиналу для неполной раздачи или самую мелкую при полной
            if not card:
                if no_full and deal_cards <= limit:
                    cards = [c for c in player.cards_sorted() if not c.joker]
                else:
                    cards = [c for c in player.cards_sorted(ascending=True) if not c.joker]

                if cards:
                    card = cards[0]
                else:
                    # это значит остался только джокер. Если мы тут - значит уже перебрали
                    # если все партнеры на данный момент взяли свое - скинем так, чтоб кто-то перебрал
                    card = player.cards[0]
                    if not no_full and all([p.order == p.take for p in self.players if p != player]):
                        card.joker_action = const.JOKER_GIVE
                        card.joker_lear = random.choice([l for l in range(len(const.LEAR_NAMES))
                                                         if not self._ai_lear_released(l)])
                    else:
                        # или просто заберем
                        card.joker_action = const.JOKER_TAKE
                        card.joker_lear = self._trump if self._trump != const.LEAR_NOTHING else random.choice(
                            [l for l in range(len(const.LEAR_NAMES))])
        else:
            # мизер или взято свое - надо скинуть:
            # ходим самой мелкой, сразу проверим, что масть этой карты еще не вышла
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

    def _ai_calc_beat_gold(self) -> int:
        """
        Вычисляет, чем покрыть карты на столе при золотой. Для случаев, когда ходишь НЕ первый.
        Возвращает индекс карты в массиве карт игрока. Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        player = self._players[self._curr_player]
        tbl_ordered = self._order_table()
        walk_lear = tbl_ordered[0][1].card.lear if not tbl_ordered[0][1].is_joker() else tbl_ordered[0][1].joker_lear()

        # предварительно заполним набор тех карт, на которые потенциально можно взять
        if not player.order_cards:
            self._ai_fill_order_to_gold(player)

        # без вариантов - надо брать - выбрать надо наименьшую на которую можно гарантированно взять
        take = False
        card = None
        cards = player.gen_lear_range(walk_lear, ascending=True)

        if not cards:
            # если масти нет - берем козырь
            cards = player.gen_lear_range(self._trump, ascending=True)

        # а дальше начнинаем увеличивать достоинство карты до тех пор, пока карта гарантированно побьет
        while not take and cards:
            card = cards.pop(0)
            # если выбранная карта не бьет то, что уже на столе или
            # мой ход не последний и что-то не вышло, что может побить это карту - ищем дальше...
            take = card == self._ai_max_card(*(ti[1].card for ti in tbl_ordered), card)

            if len(self._table) < self.party_size() - 1:
                # если я хожу не последний - проверить, что вышло все, что больше, и что не вышла масть
                # или вышла с козырем
                take = take and self._ai_can_take(card)

        if not take:
            # всетаки не беру на найденную - просто выберем самую мелкую заданной масти (или козрь)
            card = player.min_card(walk_lear) or player.min_card(self._trump)

            # посмотрим - не просираем ли мы карту, на которую рассчитывали, если да - кинем джокера
            if card in player.order_cards:
                n = player.index_of_card(joker=True)
                if n > -1:
                    card = player.cards[n]
                    take = True

        # если выбранная карта не берет, но при этом оставшиеся карты гарантированно берут при условии,
        # что ходишь первый - кидаем джокера, чтобы перехватить ход
        if not take:
            n = player.index_of_card(joker=True)
            if n > -1:
                if len([c for c in player.cards if self._ai_can_take(c, False)]) == len(player.cards):
                    card = player.cards[n]

        # масти нет и козыря нет, джокера не задействовали - надо выбрать что-то ненужное другой масти;
        # при выборе постараемся исключить те, на которые рассчитывали, если возможно
        if not card:
            cards = [c for c in player.cards_sorted(ascending=True)
                     if c not in player.order_cards and not c.joker]
            if not cards:
                cards = [c for c in player.cards_sorted(ascending=True) if not c.joker]

            if cards:
                card = cards[0]
                if card in player.order_cards:
                    # если на карту расчитывали, есть джокер и ее возможно прикрыть - кидаем джокера
                    n = player.index_of_card(joker=True)
                    if n > -1:
                        if self._ai_lear_exists_or_over_safe(card.lear) and self._ai_greater_cards_count(card) - 1 <= 0:
                            card = player.cards[n]
            else:
                # это значит остался только джокер
                card = player.cards[0]

        if card.joker:
            card.joker_action = const.JOKER_TAKE
            card.joker_lear = self._trump if self._trump != const.LEAR_NOTHING else walk_lear

        return player.cards.index(card)

    def _ai_calc_beat(self) -> int:
        """
        Вычисляет, чем покрыть карты на столе. Для случаев, когда ходишь НЕ первый.
        Возвращает индекс карты в массиве карт игрока. Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        player = self._players[self._curr_player]
        tbl_ordered = self._order_table()
        deal_type = self._deals[self._curr_deal].type_
        walk_lear = tbl_ordered[0][1].card.lear if not tbl_ordered[0][1].is_joker() else tbl_ordered[0][1].joker_lear()

        if tbl_ordered[0][1].is_joker() and tbl_ordered[0][1].joker_action() == const.JOKER_TAKE_BY_MAX and self._joker_demand_peak:
            # если требовали по старшей - придется вернуть старшую
            card = player.max_card(walk_lear)
            if card:
                return player.cards.index(card)

        if deal_type == const.DEAL_GOLD:
            return self._ai_calc_beat_gold()

        if deal_type != const.DEAL_MIZER and player.order != player.take:
            # или еще не набрал или уже перебрал - надо брать: берем самую большую заданной масти
            take = False
            card = player.max_card(walk_lear)

            if not card:
                # если масти нет - берем самый большой козырь
                card = player.max_card(self._trump)

            if card:
                # если самая большая моя не бьет то, что уже на столе или
                # мой ход не последний и что-то не вышло, что может побить это карту - ищем дальше...
                take = card == self._ai_max_card(*(ti[1].card for ti in tbl_ordered), card)

                if len(self._table) < self.party_size() - 1:
                    # если я хожу не последний - проверить, что вышло все, что больше, и что не вышла масть
                    # или вышла с козырем
                    take = take and self._ai_can_take(card)

                if not take:
                    # всетаки не беру на найденную - выбираю самую мелкую (масти или козырь, в зависимости от наличия масти)
                    card = player.min_card(walk_lear) or player.min_card(self._trump)

                    # посмотрим - не просираем ли мы карту, на которую рассчитывали, если да - кинем джокера
                    if card in player.order_cards:
                        n = player.index_of_card(joker=True)
                        if n > -1:
                            # надо учесть момент, что если мы набрали на что-то, на что не рассчитывали,
                            # то какие-то карты из тех, на что рассчитывали будут лишними, а значит это можно отдать пока
                            # их кол-ва не станет столько, солько осталось взять взяток, а то так можно и перебрать потом.
                            if player.order - player.take <= len([c for c in player.cards if c in player.order_cards]):
                                card = player.cards[n]
                                take = True

            # если уже срочно пора брать, иначе просто не хватит карт, чтоб набрать - кинем джокера
            if not take and (player.order - player.take) >= len(player.cards):
                n = player.index_of_card(joker=True)
                if n > -1:
                    card = player.cards[n]

            # масти нет и козыря нет, джокера не задействовали - надо выбрать что-то ненужное другой масти;
            # если игрок еще не набрал свое - при выборе постараемся исключить те, на которые рассчитывали, если возможно
            if not card:
                cards = []
                if self._ai_player_take_poor(player):
                    cards = [c for c in player.cards_sorted(ascending=True)
                             if c not in player.order_cards and not c.joker]
                if not cards:
                    cards = [c for c in player.cards_sorted(ascending=True) if not c.joker]

                if cards:
                    card = cards[0]
                else:
                    # это значит остался только джокер
                    card = player.cards[0]

            if card.joker:
                card.joker_action = const.JOKER_TAKE
                card.joker_lear = self._trump if self._trump != const.LEAR_NOTHING else walk_lear
        else:
            # свое взято - надо сливать - слить надо самую крупную из возможных
            card = None
            take = False

            # находим самую большую из тех, на которую точно не возьмешь
            # и точно такая же логика для козыря
            for lear in (walk_lear, self._trump):
                if lear == const.LEAR_NOTHING:
                    continue

                take = False

                for c in player.gen_lear_range(lear):
                    card = c
                    take = card == self._ai_max_card(*(ti[1].card for ti in tbl_ordered), card)
                    if not take:
                        if len(tbl_ordered) < self.party_size() - 1:
                            take = not self._ai_can_give(card)  # self._ai_can_take(card)
                        if not take:
                            break

                # если всетаки бьем - найденная будет самой маленькой картой этой масти из моих
                # если походили все, кроме меня: на мизере берем самую большую, в остальных - так и оставляем,
                # потому что если не мизер - то дальше наша стратегия - набрать как можно больше.
                # если походили не все - оставляем маленькую - это шанс, что у кого-то есть больше
                if take:
                    if len(tbl_ordered) == self.party_size() - 1:
                        if deal_type == const.DEAL_MIZER:
                            card = player.max_card(lear)

                if card:
                    break

            # а теперь посмотрим - если есть серьезный шанс взять - кинем джокера (если он есть конечно)
            if take:
                n = player.index_of_card(joker=True)
                if n > -1:
                    card = player.cards[n]

            # нет ни масти ни козыря (и джокер не понадобился)
            if not card:
                # выкинуть самую большую из имеющихся, выбрать надо такую масть, по которой у нас на руках
                # хуже всего дела с мелкими картами
                # отранжируем масти по степени фиговости дел с мелочью
                lears = {l: 0 for l in range(len(const.LEAR_NAMES)) if player.lear_exists(l)}
                for l in lears:
                    lears[l] = sum([c.value for c in player.gen_lear_range(l, True) if c.value < 9]) or 100

                if lears:
                    lears = list(lears.items())
                    # перемешаем масти, чтобы при равных весах не выпадал всегда один и тот же порядок
                    random.shuffle(lears)
                    lears = sorted(lears, key=lambda el: el[1], reverse=True)
                    card = player.gen_lear_range(lears[0][0])[0]
                else:
                    # тут вариант один - остался только один джокер
                    card = player.cards[0]

            if card.joker:
                card.joker_action = const.JOKER_GIVE
                card.joker_lear = card.lear if self._joker_give_at_par else walk_lear

        return player.cards.index(card)
