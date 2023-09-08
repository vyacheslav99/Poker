""" Реализация механизмов ИИ на базе игрового движка. ИИ читерского уровня """
# todo: Модуль недописан!

import random

from core import const, base
from core.helpers import flip_coin


class Engine(base.BaseEngine):

    def __init__(self, players: list, **options):
        super(Engine, self).__init__(players, **options)

    # --==** Реализация движка ИИ **==--

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
            # тут в раздаче всегда 1 карта
            is_dark = False
            b = True

            for p in self._players:
                if p != player:
                    if p.cards[0].joker and p.order in (-1, 1):
                        b = False
                    elif p.cards[0].lear == self._trump:
                        if p.cards[0].value > player.cards[0].value:
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

    def _ai_calc_walk(self) -> int:
        """
        Вычисляет, чем походить. Для случаев, когда ходишь первый. Возвращает индекс карты в массиве карт игрока.
        Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        player = self._players[self._curr_player]
        card = random.choice(player.cards)

        if card.joker:
            card.joker_action = random.randint(0, 2)
            card.joker_lear = random.randrange(len(const.LEAR_NAMES))

        return player.cards.index(card)

    def _ai_calc_beat(self) -> int:
        """
        Вычисляет, чем покрыть карты на столе. Для случаев, когда ходишь НЕ первый.
        Возвращает индекс карты в массиве карт игрока. Обязательно вернет какую-нибудь карту, т.к. игрок обязан походить
        """

        player = self._players[self._curr_player]
        tbl_ordered = self._order_table()
        walk_lear = tbl_ordered[0][1].card.lear if not tbl_ordered[0][1].is_joker() else tbl_ordered[0][1].joker_lear()

        if tbl_ordered[0][1].is_joker() and tbl_ordered[0][1].joker_action() == const.JOKER_TAKE_BY_MAX and self._joker_demand_peak:
            card = player.max_card(walk_lear)
            if card:
                return player.cards.index(card)

        cards = player.gen_lear_range(walk_lear)
        if not cards and self._trump:
            cards = player.gen_lear_range(self._trump)
        if not cards:
            cards = player.cards

        card = random.choice(cards)

        if card.joker:
            card.joker_action = random.randint(0, 2)
            card.joker_lear = random.randrange(len(const.LEAR_NAMES))

        return player.cards.index(card)
