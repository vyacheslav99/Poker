""" Простой консольный клиент для игры. Для тестирования игрового движка """

import os
import random

from game import engine, helpers, const


class Game():

    def __init__(self):
        self.options = {}
        self.players = []
        self.bet = None

    def set_default(self):
        self.options['game_sum_by_diff'] = True
        self.options['dark_allowed'] = True
        self.options['third_pass_limit'] = False
        self.options['fail_subtract_all'] = False
        self.options['no_joker'] = False
        self.options['strong_joker'] = True
        self.options['joker_demand_peak'] = True
        self.options['pass_factor'] = 5
        self.options['gold_mizer_factor'] = 15
        self.options['dark_notrump_factor'] = 20
        self.options['brow_factor'] = 50
        self.options['dark_mult'] = 2
        self.options['gold_mizer_on_null'] = True
        self.options['on_all_order'] = True
        self.options['take_block_bonus'] = True

    def poll_of_agreements(self):
        """ Опросить о договоренностях на игру """
        print('Перед началом игры надо кое о чем договориться')
        self.skip_lines(1)

        # 1. Игроки
        self.players = []
        player_cnt = int(self.ask('Сколько будет игроков?'))

        for i in range(player_cnt):
            if i == 0:
                self.players.append(helpers.Player())
                self.players[i].id = i
                self.players[i].is_robot = False
                self.players[i].name = self.ask('Как звать-то тебя?')
                print(f'Тебя зовут: {self.players[i].name}')
                print('Теперь давай заполним остальных игроков...')
            else:
                self.players.append(helpers.Player())
                self.players[i].id = i
                self.players[i].is_robot = self.ask(f'Игрок {i+1} человек (д/Н)?').lower() != 'д'
                self.players[i].name = self.ask(f'И как его зовут (по умолчанию "Игрок {i+1}")?') or f'Игрок {i+1}'
                if self.players[i].is_robot:
                    self.players[i].risk_level = random.randint(0, 2)
                    self.players[i].level = random.randint(0, 2)
                print(f'Игрок {i+1}: {self.players[i]}')

            print('')

        print(f'Игроков в игре: {len(self.players)}')
        self.skip_lines(1)

        # 2. Ставка
        self.bet = int(self.ask('Ставка на игру (стоимость одного очка в копейках) (1):') or 1)
        print(f'Ставка: {self.bet} коп')

        # 3. Раздачи
        self.options = {}

        if self.ask('Хочешь выбрать, какие раздачи будут в игре (по умолчанию будут присутсвовать все) (д/Н)?').lower() == 'д':
            print('Сейчас будут перечисляться названия раздач. Если надо исключить какую-то - отвечай "н", иначе она будет включена')
            self.skip_lines(1)
            deals = []

            for n in range(len(const.DEAL_NAMES)):
                if n == 1 or self.ask(const.DEAL_NAMES[n]).lower() != 'н':
                    deals.append(n)
        else:
            deals = [n for n in range(len(const.DEAL_NAMES))]

        self.options['deal_types'] = deals
        print('Включены раздачи: {0}'.format(', '.join([const.DEAL_NAMES[n] for n in deals])))
        self.skip_lines(1)

        if self.ask('Хочешь настроить остальные договоренности (д) или установить стандартные (Н)?').lower() != 'д':
            self.set_default()
            return

        # 4. Опции игры
        self.options['game_sum_by_diff'] = self.ask('Как будем считать итоги игры? Все отдают друг другу ("1") или все отдают тому, кто больше набрал ("2")?') == '1'
        print('Подсчет итогов: {0}'.format('Все расчитываются со всеми' if self.options['game_sum_by_diff'] else 'Все отдают тому, у кого больше всех'))
        self.options['dark_allowed'] = self.ask('Разрешить заказывать в темную? (Д/н)').lower() != 'н'
        print('Заказ в темную: {0}'.format('Разрешен' if self.options['dark_allowed'] else 'Запрещен'))
        self.options['third_pass_limit'] = self.ask('Включить ограничение на 3 паса подряд? (д/Н)').lower() == 'д'
        print('Ограничение на 3 паса подряд: {0}'.format('Включено' if self.options['third_pass_limit'] else 'Не ограничено'))
        self.options['fail_subtract_all'] = self.ask('Как считать недоборы: вычитать весь заказ ("1") или вычитать разницу между заказом и взятым ("2"?').lower() == '1'
        print('Вычет недоборов: {0}'.format('Весь заказ' if self.options['fail_subtract_all'] else 'Разница между заказом и взятым'))
        self.options['no_joker'] = self.ask('Играем с джокером? (Д/н)').lower() == 'н'
        print('Джокер в игре: {0}'.format('Отключен' if self.options['no_joker'] else 'Включен'))

        if not self.options['no_joker']:
            self.options['strong_joker'] = self.ask('Джокер играет строго по масти (не бьет козыря, если он не выдан за козыря)? (Д/н)').lower() != 'н'
            print('Джокер строго по масти: {0}'.format('Да' if self.options['strong_joker'] else 'Нет'))
            self.options['joker_demand_peak'] = self.ask('Джокер может требовать выдать "по старшей / младшей карте масти"? (Д/н)').lower() != 'н'
            print('Джокер может требовать старшую/младшую: {0}'.format('Да' if self.options['joker_demand_peak'] else 'Нет'))
        else:
            self.options['strong_joker'] = False
            self.options['joker_demand_peak'] = False

        print(f"Очки за сыграную взятку в обычной игре: {10}")
        print(f"Очки за взятку при переборе: {1}")
        print(f"Очки за взятку при недоборе: {-10}")
        self.options['pass_factor'] = int(self.ask('Очки за сыгранный пас (5):') or 5)
        print(f"Очки за пас: {self.options['pass_factor']}")
        self.options['gold_mizer_factor'] = int(self.ask('Очки за взятку на золотой / мизере (для мизера будет это число с минусом) (15):') or 15)
        print(f"Очки за взятку на золотой/мизере: {self.options['gold_mizer_factor']}/{-self.options['gold_mizer_factor']}")
        self.options['dark_notrump_factor'] = int(self.ask('Очки за взятку на бескозырке и темной (20):') or 20)
        print(f"Очки за взятку на бескозырке и темной: {self.options['dark_notrump_factor']}")
        self.options['brow_factor'] = int(self.ask('Очки за взятку в лобовой (50):') or 50)
        print(f"Очки за взятку в лобовой: {self.options['brow_factor']}")
        self.options['dark_mult'] = int(self.ask('Умножать очки при заказе в темную на (2):') or 2)
        print(f"При заказе в темную очки умножаются на: {self.options['dark_mult']}")

        self.options['gold_mizer_on_null'] = self.ask('Включить премию/штраф за 0 взяток на мизере/золотой? (Д/н)').lower() != 'н'
        print('Премия/штраф за 0 взяток на мизере/золотой: {0}'.format('Включена' if self.options['gold_mizer_on_null'] else 'Отключена'))
        self.options['on_all_order'] = self.ask('Удваивать очки если заказ равен кол-ву карт (кроме одной)? (Д/н)').lower() != 'н'
        print('Удвоение очков при заказе всех карт: {0}'.format('Включено' if self.options['on_all_order'] else 'Отключено'))
        self.options['take_block_bonus'] = self.ask('Включить премию за то, что взял заказ во всех раундах блока? (Д/н)').lower() != 'н'
        print('Премя за сыгранные все игры блока: {0}'.format('Включена' if self.options['take_block_bonus'] else 'Отключена'))

    def skip_lines(self, n):
        for _ in range(n):
            print('')

    def ask(self, question):
        print(question)
        return input()

    def print_options(self):
        print(f'Игроков в игре: {len(self.players)}')
        print('Включены раздачи: {0}'.format(', '.join([const.DEAL_NAMES[n] for n in self.options['deal_types']])))
        print(f'Ставка: {self.bet} коп')
        print('Подсчет итогов: {0}'.format('Все расчитываются со всеми' if self.options['game_sum_by_diff'] else 'Все отдают тому, у кого больше всех'))
        print('Заказ в темную: {0}'.format('Разрешен' if self.options['dark_allowed'] else 'Запрещен'))
        print('Ограничение на 3 паса подряд: {0}'.format('Включено' if self.options['third_pass_limit'] else 'Не ограничено'))
        print('Вычет недоборов: {0}'.format('Весь заказ' if self.options['fail_subtract_all'] else 'Разница между заказом и взятым'))
        print('Джокер в игре: {0}'.format('Отключен' if self.options['no_joker'] else 'Включен'))

        if not self.options['no_joker']:
            print('Джокер строго по масти: {0}'.format('Да' if self.options['strong_joker'] else 'Нет'))
            print('Джокер может требовать старшую/младшую: {0}'.format('Да' if self.options['joker_demand_peak'] else 'Нет'))

        print(f"Очки за сыграную взятку в обычной игре: {10}")
        print(f"Очки за взятку при переборе: {1}")
        print(f"Очки за взятку при недоборе: {-10}")
        print(f"Очки за пас: {self.options['pass_factor']}")
        print(f"Очки за взятку на золотой/мизере: {self.options['gold_mizer_factor']}/{-self.options['gold_mizer_factor']}")
        print(f"Очки за взятку на бескозырке и темной: {self.options['dark_notrump_factor']}")
        print(f"Очки за взятку в лобовой: {self.options['brow_factor']}")
        print(f"При заказе в темную очки умножаются на: {self.options['dark_mult']}")

        print('Премия/штраф за 0 взяток на мизере/золотой: {0}'.format('Включена' if self.options['gold_mizer_on_null'] else 'Отключена'))
        print('Удвоение очков при заказе всех карт: {0}'.format('Включено' if self.options['on_all_order'] else 'Отключено'))
        print('Премя за сыгранные все игры блока: {0}'.format('Включена' if self.options['take_block_bonus'] else 'Отключена'))

    def print_round_info(self, ge):
        """ Вывести: Номер и название раздачи, кол-во карт, козырь """
        self.skip_lines(1)
        d = ge.current_deal()
        print(f'Раздача {const.DEAL_NAMES[d.type_]} < по {d.cards} >')
        print('Козырь: {0}'.format('нет' if ge.trump() == const.LEAR_NOTHING else const.LEAR_NAMES[ge.trump()]))
        print(f'Первый ходит: {d.player.name}')

    def go(self):
        try:
            while True:
                try:
                    self.poll_of_agreements()
                    self.skip_lines(1)

                    if self.ask('ОК, готово. Хочешь просмотреть заданные договоренности (д/Н)').lower() == 'д':
                        self.print_options()

                    if self.ask('ОК, все готово. Приступаем к игре (Д/н)').lower() != 'н':
                        break

                    if self.ask('Хочешь настроить заново (Д) или выйти (н)').lower() == 'н':
                        return
                except Exception as e:
                    print('Ну блин, что за лажа? Теперь начинать заново')

            is_new_round = True  # первый круг после начала раунда
            ge = engine.Engine(self.players, self.bet, **self.options)
            ge.start()

            while ge.started():
                if is_new_round:
                    is_new_round = False
                    self.print_round_info(ge)

                if ge.status() == const.EXT_STATE_WALKS:
                    if ge.is_bet():
                        print('Делаем заказы на раунд')
                        n, p = ge.walk_player()

                        for i, pl in enumerate(ge.players):
                            if i != n and pl.order > -1:
                                print(f'{pl.name}: {pl.order}')

                        while True:
                            order = self.ask(f'{p.name}, твой заказ:')
                            try:
                                ge.make_order(order)
                                break
                            except helpers.GameException as e:
                                print(e)
                    else:
                        pass

        except KeyboardInterrupt:
            return


def main():
    Game().go()

if __name__ == '__main__':
    main()
