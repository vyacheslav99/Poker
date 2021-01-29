from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const
from modules.core import const as eng_const


class AgreementsDialog(QDialog):

    def __init__(self, parent, agreements: dict):
        super().__init__(parent)
        self._agreements = agreements

        # элементы управления
        self._btn_ok = None
        self._game_sum_by_diff = None       # подведение итогов игры: по разнице между игроками (0) или по старшим очкам (1)
        self._dark_allowed = None           # вкл/выкл возможность заказывать в темную в обычных раздачах
        self._third_pass_limit = None       # вкл/выкл ограничение на 3 паса подряд
        self._fail_subtract_all = None      # способ расчета при недоборе: True - минусовать весь заказ / False - минусовать только не взятые
        self._no_joker = None               # игра без джокеров вкл/выкл
        self._joker_give_at_par = None      # вариант сброса джокера: True: по номиналу (как 7 пик) или по выбору игрока
        self._joker_demand_peak = None      # джокер может/нет требовать "по старшей карте масти"
        self._pass_factor = None            # очки за сыгранный пас
        self._gold_mizer_factor = None      # очки за взятку на золотой/мизере
        self._dark_notrump_factor = None    # очки за сыгранную взятку на темной/бескозырке
        self._brow_factor = None            # очки за сыгранную взятку на лобовой
        self._dark_mult = None              # множитель для темной
        self._gold_mizer_on_null = None     # вкл/выкл штраф/бонус за 0 взяток на золоте/мизере
        self._on_all_order = None           # вкл/выкл бонус/штраф, если заказ = кол-ву карт в раздаче и взял/не взял
        self._take_block_bonus = None       # вкл/выкл приемию за сыгранные все раунды блока
        self._bet = None                    # ставка на игру (стоимость одного очка в копейках)
        self._players_cnt = None            # количество игроков
        self._deal_types = None             # типы раздач

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/list.png'))
        self.setWindowTitle('Игровые договоренности')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self.set_agreements()

    def init_ui(self):
        # Кнопки ОК, Отмена
        main_layout = QVBoxLayout()
        self._btn_ok = QPushButton(QIcon(f'{const.RES_DIR}/ok.png'), 'OK')
        self._btn_ok.setDefault(True)
        self._btn_ok.setFixedWidth(140)
        self._btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton(QIcon(f'{const.RES_DIR}/cancel.png'), 'Отмена')
        btn_cancel.setFixedWidth(140)
        btn_cancel.clicked.connect(self.reject)
        buttons_box = QHBoxLayout()
        buttons_box.addWidget(self._btn_ok)
        buttons_box.addWidget(btn_cancel)

        # Кол-во игроков, ставка и прочие самостоятельне опции
        group = QGroupBox()
        layout = QGridLayout()
        layout.setHorizontalSpacing(20)
        l2 = QHBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Количество участников парии  '))
        self._players_cnt = QSpinBox()
        self._players_cnt.setMinimum(3)
        self._players_cnt.setMaximum(4)
        self._players_cnt.setFixedWidth(50)
        l2.addWidget(self._players_cnt)
        layout.addLayout(l2, 1, 1, Qt.AlignLeft)

        l2 = QHBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Ставка на игру, коп  '))
        self._bet = QSpinBox()
        self._bet.setMinimum(1)
        self._bet.setFixedWidth(70)
        self._bet.setToolTip('Стоимость одного очка в копейках для вычисления суммы выигрыша при рассчете итогов игры')
        l2.addWidget(self._bet)
        layout.addLayout(l2, 2, 1, Qt.AlignLeft)

        self._dark_allowed = QCheckBox('Разрешить заказ в темную (в обычных партиях)')
        layout.addWidget(self._dark_allowed, 1, 2)
        self._third_pass_limit = QCheckBox('Запретить пасовать 3 раза подряд')
        layout.addWidget(self._third_pass_limit, 2, 2)
        group.setLayout(layout)
        main_layout.addWidget(group)

        # Вкл/выкл раздач в игре
        group = QGroupBox('Раздачи')
        layout = QGridLayout()
        self._deal_types = QButtonGroup()
        self._deal_types.setExclusive(False)
        r = 1
        c = 1
        for i in range(len(eng_const.DEAL_NAMES)):
            if i % 2 == 0:
                c += 1
                r = 1
            chb = QCheckBox(eng_const.DEAL_NAMES[i])
            chb.setEnabled(i != 1)
            self._deal_types.addButton(chb, id=i)
            layout.addWidget(chb, r, c)
            r += 1

        group.setLayout(layout)
        main_layout.addWidget(group)

        # Все, что касается подсчета очков (кроме премий / штрафов)
        group = QGroupBox('Подсчет очков')
        layout = QGridLayout()
        layout.setHorizontalSpacing(20)

        layout.addWidget(QLabel('Способ рассчета выигрыша'), 1, 1)
        self._game_sum_by_diff = QComboBox()
        self._game_sum_by_diff.setEditable(False)
        self._game_sum_by_diff.setFixedWidth(230)
        self._game_sum_by_diff.setToolTip('<ul><li>Каждый с каждым: '
                                          'Каждый игрок рассчитывается с каждым: тот, у кого меньше очков отдает разницу тому, '
                                          'у кого больше. После этого подводится общий итог по каждому игроку. '
                                          'В итоге несколько игроков может оказаться в плюсе.</li><li>'
                                          'Только с победителем: Каждый игрок рассчитывается только с набравшим больше всех очков - '
                                          'отдает ему разницу между своими и его очками. В итоге в плюсе остается только игрок, '
                                          'набравший больше всех очков.</li></ul>')
        self._game_sum_by_diff.addItem('Каждый с каждым')
        self._game_sum_by_diff.addItem('Только с победителем')
        layout.addWidget(self._game_sum_by_diff, 2, 1)

        layout.addWidget(QLabel('Как вычитать недоборы'), 1, 2)
        self._fail_subtract_all = QComboBox()
        self._fail_subtract_all.setEditable(False)
        self._fail_subtract_all.setFixedWidth(230)
        self._fail_subtract_all.setToolTip('<ul><li>Весь заказ: вычитать сумму всего заказа</li>'
                                           '<li>Только не взятое: вычитать разницу между заказом и взятым</li></ul>')
        self._fail_subtract_all.addItem('Весь заказ')
        self._fail_subtract_all.addItem('Только не взятое')
        layout.addWidget(self._fail_subtract_all, 2, 2)

        l2 = QHBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Очки за сыгранный пас  '))
        self._pass_factor = QSpinBox()
        self._pass_factor.setMinimum(1)
        self._pass_factor.setFixedWidth(70)
        l2.addWidget(self._pass_factor)
        layout.addLayout(l2, 3, 1, Qt.AlignLeft)

        l2 = QHBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Очки за взятку на золотой / мизере  '))
        self._gold_mizer_factor = QSpinBox()
        self._gold_mizer_factor.setMinimum(1)
        self._gold_mizer_factor.setFixedWidth(70)
        l2.addWidget(self._gold_mizer_factor)
        layout.addLayout(l2, 3, 2, Qt.AlignLeft)

        l2 = QHBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Очки за сыгранную взятку на темной / бескозырке  '))
        self._dark_notrump_factor = QSpinBox()
        self._dark_notrump_factor.setMinimum(1)
        self._dark_notrump_factor.setFixedWidth(70)
        l2.addWidget(self._dark_notrump_factor)
        layout.addLayout(l2, 4, 1, Qt.AlignLeft)

        l2 = QHBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Очки за сыгранную взятку на лобовой  '))
        self._brow_factor = QSpinBox()
        self._brow_factor.setMinimum(1)
        self._brow_factor.setFixedWidth(70)
        l2.addWidget(self._brow_factor)
        layout.addLayout(l2, 4, 2, Qt.AlignLeft)

        l2 = QHBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Умножать взятки на темной на  '))
        self._dark_mult = QSpinBox()
        self._dark_mult.setMinimum(1)
        self._dark_mult.setFixedWidth(70)
        l2.addWidget(self._dark_mult)
        layout.addLayout(l2, 5, 1, Qt.AlignLeft)

        group.setLayout(layout)
        main_layout.addWidget(group)

        # Премии и штрафы
        group = QGroupBox('Премии / штрафы')
        layout = QGridLayout()
        self._gold_mizer_on_null = QCheckBox('Премия / штраф за 0 взяток на Золотой / Мизере')
        layout.addWidget(self._gold_mizer_on_null, 1, 1)
        self._on_all_order = QCheckBox('Премия / штраф за заказ равный количеству карт на руках')
        layout.addWidget(self._on_all_order, 2, 1)
        self._take_block_bonus = QCheckBox('Премия если сыграл все игры блока (например все темные)')
        layout.addWidget(self._take_block_bonus, 1, 2)
        group.setLayout(layout)
        main_layout.addWidget(group)

        # Все, что касается Джокера
        group = QGroupBox('Джокер')
        layout = QGridLayout()
        layout.setHorizontalSpacing(30)
        self._no_joker = QCheckBox('Игра без Джокера')
        self._no_joker.stateChanged.connect(self.no_joker_check)
        layout.addWidget(self._no_joker, 1, 1)
        self._joker_give_at_par = QCheckBox('Сброс Джокера по номиналу (как 7 ♠) (или на выбор игрока)')
        layout.addWidget(self._joker_give_at_par, 2, 1)
        self._joker_demand_peak = QCheckBox('Джокер может требовать "по старшей карте"')
        layout.addWidget(self._joker_demand_peak, 2, 2)
        group.setLayout(layout)
        main_layout.addWidget(group)

        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)

    def set_agreements(self, agreements: dict=None):
        if agreements:
            self._agreements = agreements

        self._game_sum_by_diff.setCurrentIndex(0 if self._agreements.get('game_sum_by_diff', True) else 1)
        self._dark_allowed.setChecked(self._agreements.get('dark_allowed', False))
        self._third_pass_limit.setChecked(self._agreements.get('third_pass_limit', False))
        self._fail_subtract_all.setCurrentIndex(0 if self._agreements.get('fail_subtract_all', False) else 1)
        self._no_joker.setChecked(self._agreements.get('no_joker', False))
        self._joker_give_at_par.setChecked(self._agreements.get('joker_give_at_par', False))
        self._joker_demand_peak.setChecked(self._agreements.get('joker_demand_peak', True))
        self._pass_factor.setValue(self._agreements.get('pass_factor', 5))
        self._gold_mizer_factor.setValue(self._agreements.get('gold_mizer_factor', 15))
        self._dark_notrump_factor.setValue(self._agreements.get('dark_notrump_factor', 20))
        self._brow_factor.setValue(self._agreements.get('brow_factor', 50))
        self._dark_mult.setValue(self._agreements.get('dark_mult', 2))
        self._gold_mizer_on_null.setChecked(self._agreements.get('gold_mizer_on_null', True))
        self._on_all_order.setChecked(self._agreements.get('on_all_order', True))
        self._take_block_bonus.setChecked(self._agreements.get('take_block_bonus', True))
        self._bet.setValue(self._agreements.get('bet', 10))
        self._players_cnt.setValue(self._agreements.get('players_cnt', 3))

        for i in range(len(eng_const.DEAL_NAMES)):
            self._deal_types.button(i).setChecked(i in self._agreements.get('deal_types', [1]))

    def get_agreements(self):
        self._agreements['game_sum_by_diff'] = self._game_sum_by_diff.currentIndex() == 0
        self._agreements['dark_allowed'] = self._dark_allowed.isChecked()
        self._agreements['third_pass_limit'] = self._third_pass_limit.isChecked()
        self._agreements['fail_subtract_all'] = self._fail_subtract_all.currentIndex() == 0
        self._agreements['no_joker'] = self._no_joker.isChecked()
        self._agreements['joker_give_at_par'] = self._joker_give_at_par.isChecked()
        self._agreements['joker_demand_peak'] = self._joker_demand_peak.isChecked()
        self._agreements['pass_factor'] = self._pass_factor.value()
        self._agreements['gold_mizer_factor'] = self._gold_mizer_factor.value()
        self._agreements['dark_notrump_factor'] = self._dark_notrump_factor.value()
        self._agreements['brow_factor'] = self._brow_factor.value()
        self._agreements['dark_mult'] = self._dark_mult.value()
        self._agreements['gold_mizer_on_null'] = self._gold_mizer_on_null.isChecked()
        self._agreements['on_all_order'] = self._on_all_order.isChecked()
        self._agreements['take_block_bonus'] = self._take_block_bonus.isChecked()
        self._agreements['bet'] = self._bet.value()
        self._agreements['players_cnt'] = self._players_cnt.value()

        self._agreements['deal_types'] = {1}
        for i in range(len(eng_const.DEAL_NAMES)):
            if self._deal_types.button(i).isChecked():
                self._agreements['deal_types'].add(i)

        self._agreements['deal_types'] = list(self._agreements['deal_types'])

        return self._agreements

    def deactivate(self):
        self._btn_ok.setEnabled(False)

    def no_joker_check(self, state):
        self._joker_give_at_par.setEnabled(state == Qt.Unchecked)
        self._joker_demand_peak.setEnabled(state == Qt.Unchecked)
