"""
Простая консольная версия игры. Для тестирования игрового движка.
"""

import sys, random

from core import helpers, const, engine

ROBOTS = ('Бендер', 'Флексо', 'Вертер', 'Робот Гедонист', 'СиТриПиО', 'R2D2', 'Громозека', 'Калькулон', 'Терминатор',
          'Птица Говорун', 'Маленький помошник Сатаны', 'Эндрю', 'Валли', 'Бамблби', 'Маленикий помошник Санты',
          'Электроник', 'Рой Батти', 'Робот Санта', 'Мюллер', 'Оптимус Прайм', 'Бишоп', 'Борман', 'Штирлиц',
          'Робокоп', 'Балбес', '790', 'Трус', 'Бывалый', 'Мегатрон', 'Шеф', 'IDDQD', 'Алиса', 'Коллега', 'Карбафос',
          'Аниматронио', 'Роберто', 'Рободьявол', 'Буратино', 'Фрай', 'Лила', 'Барт', 'Сыроежкин', 'Весельчак У',
          'Гомер', 'Адам Вест', 'Кот Базилио', 'Лиса Алиса', 'Мойша', 'Абрам', 'Сара', 'Гоги')

HUMANS = ('Чубрик', 'Чел', 'Колян', 'Чувак', 'Толик', 'Маня', 'Фекла', 'Вася', 'Ваня', 'Дуня')


class Game:

    def __init__(self, autogame=False):
        if autogame:
            print('Игра запущена в режиме битвы машин! ;-)')

        self.autogame = autogame
        self.options = {}
        self.players = []
        self.game = None

    def set_default(self):
        self.options['game_sum_by_diff'] = True
        self.options['dark_allowed'] = False
        self.options['third_pass_limit'] = False
        self.options['fail_subtract_all'] = False
        self.options['no_joker'] = False
        self.options['joker_give_at_par'] = False
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
        auto = self.ask('Хочешь настроить игроков сам (д) или накидать автоматически (Н)?').lower() not in ('д', 'y')
        robots = [r for r in ROBOTS]
        humans = [h for h in HUMANS]

        for i in range(player_cnt):
            if i == 0 and not self.autogame:
                self.players.append(helpers.Player())
                self.players[i].uid = i
                self.players[i].is_robot = False
                self.players[i].name = self.ask('Как звать-то тебя?') or f'{humans.pop(random.randrange(0, len(humans)))}'
                print(f'Тебя зовут: {self.players[i].name}')
                print('Теперь давай заполним остальных игроков...')
            else:
                self.players.append(helpers.Player())
                self.players[i].uid = i
                if auto:
                    self.players[i].is_robot = True
                    self.players[i].name = f'{robots.pop(random.randrange(0, len(robots)))}'
                else:
                    self.players[i].is_robot = self.ask(f'Игрок {i+1} человек (д/Н)?').lower() not in ('д', 'y')
                    self.players[i].name = self.ask(f'И как его зовут?') or \
                        f'{robots.pop(random.randrange(0, len(robots)))}' \
                        if self.players[i].is_robot else f'{humans.pop(random.randrange(0, len(humans)))}'
                if self.players[i].is_robot:
                    self.players[i].risk_level = random.randint(0, 2)
                    # self.players[i].level = random.randint(0, 2)
                print(f'Игрок {i+1}: {self.players[i]}')

            print('')

        print(f'Игроков в игре: {len(self.players)}')
        self.skip_lines(1)

        # 2. Ставка
        self.options['bet'] = int(self.ask('Ставка на игру (стоимость одного очка в копейках) (1):') or 1)
        print(f"Ставка: {self.options['bet']} коп")

        # 3. Раздачи
        self.options = {}

        if self.ask('Хочешь выбрать, какие раздачи будут в игре (по умолчанию будут присутсвовать все) (д/Н)?').lower() in ('д', 'y'):
            print('Сейчас будут перечисляться названия раздач. Если надо исключить какую-то - отвечай "н", иначе она будет включена')
            self.skip_lines(1)
            deals = []

            for n in range(len(const.DEAL_NAMES)):
                if self.ask(const.DEAL_NAMES[n]).lower() not in ('н', 'n'):
                    deals.append(n)
        else:
            deals = [n for n in range(len(const.DEAL_NAMES) - 1)]

        self.options['deal_types'] = deals
        print('Включены раздачи: {0}'.format(', '.join([const.DEAL_NAMES[n] for n in deals])))
        self.skip_lines(1)

        if self.ask('Хочешь настроить остальные договоренности (д) или установить стандартные (Н)?').lower() not in ('д', 'y'):
            self.set_default()
            return

        # 4. Опции игры
        self.options['game_sum_by_diff'] = self.ask('Как будем считать итоги игры? Все отдают друг другу ("1") или все отдают тому, кто больше набрал ("2")?') == '1'
        print('Подсчет итогов: {0}'.format('Все расчитываются со всеми' if self.options['game_sum_by_diff'] else 'Все отдают тому, у кого больше всех'))
        self.options['dark_allowed'] = self.ask('Разрешить заказывать в темную? (Д/н)').lower() not in ('н', 'n')
        print('Заказ в темную: {0}'.format('Разрешен' if self.options['dark_allowed'] else 'Запрещен'))
        self.options['third_pass_limit'] = self.ask('Включить ограничение на 3 паса подряд? (д/Н)').lower() in ('д', 'y')
        print('Ограничение на 3 паса подряд: {0}'.format('Включено' if self.options['third_pass_limit'] else 'Не ограничено'))
        self.options['fail_subtract_all'] = self.ask('Как считать недоборы: вычитать весь заказ ("1") или вычитать разницу между заказом и взятым ("2")?').lower() == '1'
        print('Вычет недоборов: {0}'.format('Весь заказ' if self.options['fail_subtract_all'] else 'Разница между заказом и взятым'))
        self.options['no_joker'] = self.ask('Играем с джокером? (Д/н)').lower() in ('н', 'n')
        print('Джокер в игре: {0}'.format('Отключен' if self.options['no_joker'] else 'Включен'))

        if not self.options['no_joker']:
            self.options['joker_give_at_par'] = self.ask('Джокер сбрасываем по номиналу (как 7 пика) или с выбором масти? (д/Н)').lower() in ('д', 'y')
            print('Сброс джокера по номиналу: {0}'.format('Да' if self.options['joker_give_at_par'] else 'Нет'))
            self.options['joker_demand_peak'] = self.ask('Джокер может требовать "по старшей карте"? (Д/н)').lower() not in ('н', 'n')
            print('Джокер может требовать "по старшей": {0}'.format('Да' if self.options['joker_demand_peak'] else 'Нет'))
        else:
            self.options['joker_give_at_par'] = False
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

        self.options['gold_mizer_on_null'] = self.ask('Включить премию/штраф за 0 взяток на мизере/золотой? (Д/н)').lower() not in ('н', 'n')
        print('Премия/штраф за 0 взяток на мизере/золотой: {0}'.format('Включена' if self.options['gold_mizer_on_null'] else 'Отключена'))
        self.options['on_all_order'] = self.ask('Удваивать очки если заказ равен кол-ву карт (кроме одной)? (Д/н)').lower() not in ('н', 'n')
        print('Удвоение очков при заказе всех карт: {0}'.format('Включено' if self.options['on_all_order'] else 'Отключено'))
        self.options['take_block_bonus'] = self.ask('Включить премию за то, что взял заказ во всех раундах блока? (Д/н)').lower() not in ('н', 'n')
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
        print(f"Ставка: {self.options['bet']} коп")
        print('Подсчет итогов: {0}'.format('Все расчитываются со всеми' if self.options['game_sum_by_diff'] else 'Все отдают тому, у кого больше всех'))
        print('Заказ в темную: {0}'.format('Разрешен' if self.options['dark_allowed'] else 'Запрещен'))
        print('Ограничение на 3 паса подряд: {0}'.format('Включено' if self.options['third_pass_limit'] else 'Не ограничено'))
        print('Вычет недоборов: {0}'.format('Весь заказ' if self.options['fail_subtract_all'] else 'Разница между заказом и взятым'))
        print('Джокер в игре: {0}'.format('Отключен' if self.options['no_joker'] else 'Включен'))

        if not self.options['no_joker']:
            print('Сброс джокера по номиналу: {0}'.format('Да' if self.options['joker_give_at_par'] else 'Нет'))
            print('Джокер может требовать "по старшей": {0}'.format('Да' if self.options['joker_demand_peak'] else 'Нет'))

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

    def print_round_info(self):
        """ Вывести: Номер и название раздачи, кол-во карт, козырь """
        self.skip_lines(1)
        d = self.game.current_deal()
        print(f'Раздача: {const.DEAL_NAMES[d.type_]} < по {d.cards} >')
        tl, tc = self.game.trump()
        print('Козырь: {0}'.format('{0}{1}'.format('нет' if tl == const.LEAR_NOTHING else f'{const.LEAR_NAMES[tl]}', f'  < {tc} >' if tc else '')))
        print(f'Первый ходит: {self.game.players[d.player].name}')

    def print_cards(self, player):
        tl, tc = self.game.trump()
        lear = ' ({0})'.format('-' if tl == const.LEAR_NOTHING else f'{const.LEAR_SYMBOLS[tl]}')
        print(f'Твои карты{lear}: ', '  '.join(['{0}{1}'.format(c, '.' if i % 3 == 0 else '') for i, c in enumerate(player.cards, 1)]))

    def get_joker_info(self, card):
        if card.joker:
            # jl = card.joker_lear if card.joker_lear is not None and card.joker_lear > -1 else card.lear
            if card.joker_action == const.JOKER_TAKE:
                s, l = 'Самая крупная', const.LEAR_SYMBOLS[card.joker_lear]
            elif card.joker_action == const.JOKER_TAKE_BY_MAX:
                s, l = 'Забираю по старшей', const.LEAR_SYMBOLS[card.joker_lear]
            elif card.joker_action == const.JOKER_GIVE:
                s, l = 'Скидываю', const.LEAR_SYMBOLS[card.joker_lear] if not self.game.joker_give_at_par else f'{card}'
            else:
                s, l = None, None

            return ' ({0} {1})'.format(s, l)
        else:
            return ''

    def print_walks(self, walk_player, after, orders):
        if after:
            f = False
            for p in self.game.lap_players_order(by_table=not orders):
                if p[0] == walk_player:
                    f = True
                if f:
                    if orders:
                        info = '{0}{1}'.format(p[0].order, ' (в темную)' if p[0].order_is_dark else '')
                    else:
                        c = self.game.table()[p[1]].card
                        info = '{0}{1}'.format(c, self.get_joker_info(c))
                    print(f'{p[0].name}: {info}')
        else:
            for p in self.game.lap_players_order(by_table=not orders):
                if p[0] == walk_player:
                    break
                if orders:
                    info = '{0}{1}'.format(p[0].order, ' (в темную)' if p[0].order_is_dark else '')
                else:
                    c = self.game.table()[p[1]].card
                    info = '{0}{1}'.format(c, self.get_joker_info(c))
                print(f'{p[0].name}: {info}')

    def print_other_cards(self, walk_player):
        for p in self.game.lap_players_order():
            if p[0] != walk_player:
                print(f'{p[0].name}: ', '  '.join([str(c) for c in p[0].cards]))

    def print_order_results(self):
        diff = sum([p.order for p in self.game.players]) - self.game.current_deal().cards
        print('{0} {1}'.format('Перебор ' if diff < 0 else 'Недобор', abs(diff)))

    def print_middle_info(self):
        print('  '.join([f'{p.name}: {p.order if p.order > -1 else "-"}{"*" if p.order_is_dark else ""} / {p.take}' for p in self.players]))

    def print_round_results(self):
        rec = self.game.get_record()
        self.skip_lines(1)
        print('Итоги раунда:')

        for player in self.game.players:
            print(f'{player.name}')
            print('    '.join([f'{rec[0][player.uid][key]}: {rec[-1][player.uid][key]}' for key in rec[0][player.uid].keys()]))

        print('-------------------------------------------------------------')

    def print_game_results(self):
        congratulations = ('УРА, Товарищи!!!', 'Ай, молодца!', 'Учитесь, сынки!')
        self.skip_lines(2)
        print('-= Итоги игры =-')
        for p in self.game.players:
            money = '{0:.2f}'.format(p.total_money)
            rub, kop = money.split('.')
            print(f'{p.name}:    {p.total_scores} :: {rub} руб {kop} коп')

        self.skip_lines(1)
        print(f'Победил {max([p for p in self.game.players], key=lambda x: x.total_money)}')
        print(random.choice(congratulations))

    def ask_joker_walk(self, card):
        actions = {
            '1': ('Забираю', const.JOKER_TAKE),
            '2': ('Скидываю', const.JOKER_GIVE),
            '3': ('Забираю по старшей карте', const.JOKER_TAKE_BY_MAX)
        }

        is_first = not self.game.table()
        print('Выбери действие джокером:')

        for a in actions:
            if a == '3' and not is_first:
                pass
            else:
                print(f'{a}. {actions[a][0]}')

        jo = self.ask('')

        if is_first:
            if jo == '2' and self.game.joker_give_at_par:
                l = card.lear
            else:
                print('Закажи масть:')
                for i, x in enumerate(const.LEAR_NAMES, 1):
                    print(f'{i}. {x}')
                l = int(self.ask('')) - 1
        else:
            ftbl = self.game.lap_players_order(by_table=True)[0]
            if jo == '1':
                l = self.game.trump()[0] if self.game.trump()[0] != const.LEAR_NOTHING else self.game.table()[ftbl[1]].card.lear
            else:
                l = card.lear if self.game.joker_give_at_par else self.game.table()[ftbl[1]].card.lear

        card.joker_action = actions[jo][1]
        card.joker_lear = l

    def go(self):
        try:
            while True:
                try:
                    self.poll_of_agreements()
                    self.skip_lines(1)

                    if self.ask('Хочешь просмотреть заданные договоренности? (д/Н)').lower() in ('д', 'y'):
                        self.print_options()

                    if self.ask('Ну что ж, все готово. Приступаем к игре? (Д/н)').lower() not in ('н', 'n'):
                        break

                    if self.ask('Хочешь настроить заново (Д) или выйти (н)').lower() in ('н', 'n'):
                        return
                except Exception as e:
                    print('Ну блин, что за лажа? Теперь начинать заново')

            is_new_round = True  # первый круг после начала раунда
            after_bet = False
            self.game = engine.Engine(self.players, allow_no_human=self.autogame, **self.options)
            self.game.start()

            while self.game.started():
                if is_new_round:
                    is_new_round = False
                    self.print_round_info()

                if self.game.status() == const.EXT_STATE_WALKS:
                    n, p = self.game.walk_player()

                    if self.game.is_bet():
                        after_bet = True
                        self.skip_lines(1)
                        print('Заказываем')
                        if self.game.dark_allowed and self.game.current_deal().type_ != const.DEAL_DARK:
                            dark = self.ask('Хочешь заказать в темную? (д/Н)').lower() in ('д', 'y')
                        else:
                            dark = False

                        # выводим заказы всех, кто до тебя
                        self.print_walks(p, False, True)
                        if self.game.current_deal().type_ == const.DEAL_BROW:
                            self.print_other_cards(p)
                        elif not dark and self.game.current_deal().type_ != const.DEAL_DARK:
                            self.print_cards(p)

                        # твой заказ
                        while True:
                            try:
                                self.game.make_order(int(self.ask(f'{p.name}, твой заказ:')), dark)
                                break
                            except helpers.GameException as e:
                                print(e)
                            except Exception as e:
                                print(f'{e}! Не дури, введи число от 0 (пас) до кол-ва карт на руках')
                    else:
                        # выводим заказы всех кто после тебя
                        if after_bet:
                            after_bet = False
                            self.print_walks(p, True, True)
                            self.print_order_results()
                            self.skip_lines(1)
                            print('Ходим')

                        # выводим карты, которые уже брошены на стол
                        self.print_walks(p, False, False)

                        # твой ход
                        self.print_cards(p)
                        while True:
                            try:
                                n = int(self.ask(f'{p.name}, твой ход:')) - 1
                                if p.cards[n].joker:
                                    self.ask_joker_walk(p.cards[n])
                                self.game.do_walk(n)
                                break
                            except helpers.GameException as e:
                                print(e)
                            except Exception as e:
                                print(f'{e}! Не дури, введи номер карты, которой хочешь походить')

                    self.game.give_walk()
                elif self.game.status() == const.EXT_STATE_LAP_PAUSE:
                    # выводим все остальные ходы
                    self.print_walks(p, True, False)

                    # выводим информацию, кто побил
                    self.skip_lines(1)
                    print(f'Взял: {self.game.take_player()[1].name}')
                    self.print_middle_info()
                    self.ask('Жми <Enter> для продолжения...')
                elif self.game.status() == const.EXT_STATE_ROUND_PAUSE:
                    # выводим итоги раунда
                    is_new_round = True
                    self.print_round_results()
                    self.ask('Жми <Enter> для продолжения...')

                self.game.next()

            # вывести итоги последнего раунда
            self.print_round_results()
            # вывести итоги игры
            self.print_game_results()
        except KeyboardInterrupt:
            print('Игра прервана...')
            return


def main():
    Game(autogame='-a' in sys.argv).go()


if __name__ == '__main__':
    main()
