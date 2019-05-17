""" Простой консольный клиент для игры. Для тестирования игрового движка """

import os
import random

from game import engine, helpers, const


class Game():

    def poll_of_agreements(self):
        """ Опросить о договоренностях на игру """
        print('Перед началом игры надо кое о чем договориться')
        print('')

        # 1. Игроки
        players = []
        player_cnt = int(input('Сколько будет игроков?'))

        for i in range(player_cnt):
            if i == 0:
                players.append(helpers.Player())
                players[i].id = i
                players[i].is_robot = False
                players[i].name = input('Как звать-то тебя?')
                print('Теперь давай заполним остальных игроков...')
            else:
                players.append(helpers.Player())
                players[i].id = i
                players[i].is_robot = input(f'Игрок {i+1} человек (д/Н)?').lower() != 'д'
                players[i].name = input(f'И как его зовут (по умолчанию "Игрок {i+1}")?') or f'Игрок {i+1}'
                if players[i].is_robot:
                    players[i].risk_level = random.randint(0, 3)
                    players[i].level = random.randint(0, 3)

            print('')

        self.players = players
        self.clear_console()

        # 2. Раздачи
        opts = {}

        if input('Хочешь выбрать, какие раздачи будут в игре (по умолчанию будут присутсвовать все) (д/Н)?').lower() == 'д':
            print('Сейчас будут перечисляться названия раздач. Если надо исключить какую-то - отвечай "н", иначе она будет включена')
            print('')
            deals = []

            for n in range(len(const.DEAL_NAMES)):
                if n == 1 or input(const.DEAL_NAMES[n]).lower() != 'н':
                    deals.append(n)
        else:
            deals = [n for n in range(len(const.DEAL_NAMES))]

        opts['deal_types'] = deals
        self.clear_console()

        # 3. Опции игры
        self.bet = int(input('Ставка на игру (стоимость одного очка в копейках) (1)') or 1)
        opts['game_sum_by_diff'] = input('Как будем считать итоги игры? Все отдают друг другу ("1") или все отдают тому, кто больше набрал ("2")') == '1'
        opts['dark_allowed'] = input('Разрешить заказывать в темную? (Д/н)').lower() != 'н'
        opts['third_pass_limit'] = input('Разрешить пасовать 3 раза подряд? (Д/н)').lower() != 'н'
        opts['fail_subtract_all'] = input('Как считать недоборы? Вычитать весь заказ ("1") или вычитать разницу между заказом и взятым ("2"').lower() == '1'
        opts['no_joker'] = input('Играем с джокером? (Д/н)').lower() == 'н'

        if not opts['no_joker']:
            opts['strong_joker'] = input('Джокер играет строго по масти (не бьет козыря, если он не выдан за козыря)? (Д/н)').lower() != 'н'
            opts['joker_demand_peak'] = input('Джокер может требовать выдать "по старшей / младшей карте масти"? (Д/н)').lower() != 'н'
            opts['joker_as_any_card'] = input('При ходе джокером обязательно назвать, за какую карту выдаешь (или можно просто сказать "Забираю / скидываю")? (Д/н)').lower() != 'н'
        else:
            opts['strong_joker'] = False
            opts['joker_demand_peak'] = False
            opts['joker_as_any_card'] = False

        opts['pass_factor'] = int(input('Очки за сыгранный пас (5)') or 5)
        opts['gold_mizer_factor'] = int(input('Очки за взятку на золотой / мизере (для мизера будет это число с минусом) (15)') or 15)
        opts['dark_notrump_factor'] = int(input('Очки за взятку на бескозырке / темной (20)') or 20)
        opts['brow_factor'] = int(input('Очки за взятку на лобовой (50)') or 50)
        opts['dark_mult'] = int(input('Умножать очки в темной на (2)') or 2)

        opts['gold_mizer_on_null'] = input('Включить премию/штраф за 0 взяток на мизере/золотой? (Д/н)').lower() != 'н'
        opts['on_all_order'] = input('Удваивать очки если заказ равен кол-ву карт (кроме одной)? (Д/н)').lower() != 'н'
        opts['take_block_bonus'] = input('Включить премию за то, что взял заказ во всех раундах блока? (Д/н)').lower() != 'н'

        self.options = opts

        res = input('ОК, все готово. Приступаем к игре (Д/н)').lower() != 'н'
        self.clear_console()
        return res

    def clear_console(self):
        os.system('cls')

    def go(self):
        try:
            while True:
                try:
                    res = self.poll_of_agreements()
                    if not res:
                        res = input('Хочешь настроить заново??? (д/Н)').lower() == 'д'
                        if not res:
                            return
                except Exception:
                    print('Ну блин, что за лажа? Теперь начинать заново')

            game = engine.Engine(self.players, self.bet, **self.options)
            game.start()

            while game.started():
                s = game.get_status()

        except KeyboardInterrupt:
            return


def main():
    Game().go()

if __name__ == '__main__':
    main()
