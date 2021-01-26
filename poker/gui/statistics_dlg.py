import os
import shutil
import string

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const
from gui.graphics import Face2
from modules.params import Profiles


class StatisticsWindow(QWidget):

    _columns_ = (('name', 'Игрок', ''), ('is_robot', 'ИИ?', 'Робот или Человек?'), ('started', 'Начато', 'Сколько партий начинал'),
                 ('completed', 'Сыграно', 'Сколько партий доиграно до конца'), ('throw', 'Брошено', 'Сколько партий брошено'),
                 ('winned', 'Выиграно', 'Сколько партий выиграно'), ('lost', 'Проиграно', 'Сколько партий проиграно'),
                 ('scores', 'Счет', 'Сумма очков за все игры'), ('money', 'Денег', 'Сумма денег за все игры'),
                 ('last_scores', 'Последний\nвыигрыш\n(очки)', 'Очки, набранные в последней игре'),
                 ('last_money', 'Последний\nвыигрыш\n(деньги)', 'Деньги, набранные в последней игре'),
                 ('best_scores', 'Лучший\nвыигрыш\n(очки)', 'Самый большой выигрыш за все игры в очках'),
                 ('best_money', 'Лучший\nвыигрыш\n(деньги)', 'Самый большой выигрыш за все игры в деньгах'),
                 ('worse_scores', 'Худший\nпроигрыш\n(очки)', 'Самый большой проигрыш за все игры в очках'),
                 ('worse_money', 'Худший\nпроигрыш\n(деньги)', 'Самый большой проигрыш за все игры в деньгах'))

    def __init__(self):
        super().__init__()
        self._profiles = None
        self._robots = None

        # элементы управления
        self._grid = None

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/player.ico'))
        self.setWindowTitle('Статистика игроков')
        self.init_ui()
        # rect = QDesktopWidget().availableGeometry(QDesktopWidget().primaryScreen())
        # print(rect.width(), rect.height())
        self.resize(*const.WINDOW_SIZE)

    def init_ui(self):
        # Кнопка Закрыть
        main_layout = QVBoxLayout()
        btn_close = QPushButton('Закрыть')
        btn_close.setDefault(True)
        btn_close.setFixedWidth(140)
        btn_close.clicked.connect(self.close)
        buttons_box = QHBoxLayout()
        buttons_box.setAlignment(Qt.AlignRight)
        buttons_box.addWidget(btn_close)

        # Собсно Таблица игроков

        self._grid = QTableWidget()
        self._grid.setColumnCount(len(self._columns_))
        # self._grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._grid.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._grid.setSelectionMode(QAbstractItemView.NoSelection)

        # шапка
        for i, value in enumerate(self._columns_):
            item = QTableWidgetItem(value[1])
            item.setToolTip(value[2])
            self._grid.setHorizontalHeaderItem(i, item)
            self._grid.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed if i > 0 else QHeaderView.Stretch)
            self._grid.horizontalHeader().resizeSection(i, 25 if i == 1 else 100)

        main_layout.addWidget(self._grid)
        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)

    def set_data(self, profiles: Profiles, robots):
        row = 0
        self._grid.setSortingEnabled(False)
        self._grid.setRowCount(0)
        self._grid.setRowCount(len(profiles.profiles) + len(robots.keys()))

        for p in profiles.profiles:
            for col, value in enumerate(self._columns_):
                if col == 0:
                    self.set_text_item(row, col, getattr(p, value[0]))
                elif col == 1:
                    self.set_bool_item(row, col, getattr(p, value[0]))
                else:
                    self.set_number_item(row, col, getattr(p, value[0]))
            row += 1

        for k, p in robots.items():
            for col, value in enumerate(self._columns_):
                if col == 0:
                    self.set_text_item(row, col, k)
                elif col == 1:
                    self.set_bool_item(row, col, True)
                else:
                    self.set_number_item(row, col, p[value[0]])
            row += 1

        self._grid.setSortingEnabled(True)
        self._grid.sortByColumn(7, Qt.DescendingOrder)

    def set_item(self, row, col, item):
        if col == 1:
            align = Qt.AlignCenter
        elif col > 1:
            align = Qt.AlignRight
        else:
            align = Qt.AlignLeft

        item.setTextAlignment(align | Qt.AlignVCenter)
        self._grid.setItem(row, col, item)

    def set_text_item(self, row, col, value, icon=None):
        item = QTableWidgetItem(str(value))
        self.set_item(row, col, item)

    def set_number_item(self, row, col, value):
        item = QTableWidgetItem(str(value))
        item.setData(Qt.EditRole, value)
        self.set_item(row, col, item)

    def set_bool_item(self, row, col, value):
        item = QTableWidgetItem()
        item.setFlags(Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if value else Qt.Unchecked)
        self.set_item(row, col, item)
