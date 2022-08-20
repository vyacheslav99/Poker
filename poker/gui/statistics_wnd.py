from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const
from gui.graphics import Face2, Avatar, GridMoneyItemDelegate
from models.params import Profiles


class StatisticsWindow(QWidget):

    _columns_ = (('name', 'Игрок', ''), ('is_robot', 'ИИ?', 'Робот или Человек?'), ('started', 'Начато', 'Сколько партий начинал'),
                 ('completed', 'Сыграно', 'Сколько партий доиграно до конца'), ('thrown', 'Брошено', 'Сколько партий брошено'),
                 ('winned', 'Выиграно', 'Сколько партий выиграно'), ('lost', 'Проиграно', 'Сколько партий проиграно'),
                 ('summary', 'Счет', 'Сумма очков за все игры'), ('total_money', 'Всего денег', 'Сумма денег за все игры'),
                 ('last_scores', 'Последний\nвыигрыш\n(очки)', 'Очки, набранные в последней игре'),
                 ('last_money', 'Последний\nвыигрыш\n(деньги)', 'Деньги, набранные в последней игре'),
                 ('best_scores', 'Лучший\nвыигрыш\n(очки)', 'Самый большой выигрыш за все игры в очках'),
                 ('best_money', 'Лучший\nвыигрыш\n(деньги)', 'Самый большой выигрыш за все игры в деньгах'),
                 ('worse_scores', 'Худший\nрезультат\n(очки)', 'Самый маленький результат за все игры в очках'),
                 ('worse_money', 'Худший\nпроигрыш\n(деньги)', 'Самый большой проигрыш за все игры в деньгах'))

    _money_cols_ = (8, 10, 12, 14)
    _bg_colors_ = ('PaleTurquoise', 'PaleTurquoise', 'PaleGreen', 'PaleGreen', 'PaleGreen', 'PaleGreen', 'PaleGreen',
                   'Gold', 'YellowGreen', 'Violet', 'Violet', 'SpringGreen', 'SpringGreen', 'Tomato', 'Tomato')

    def __init__(self):
        super().__init__()
        self._profiles = None
        self._robots = None
        self._curr_uid = None

        # элементы управления
        self._grid = None

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/player.ico'))
        self.setWindowTitle('Таблица результатов')
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

        self._grid = QTableWidget(self)
        self._grid.setColumnCount(len(self._columns_))
        # self._grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._grid.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._grid.setSelectionMode(QAbstractItemView.NoSelection)
        self._grid.setIconSize(QSize(64, 64))
        vhead = self._grid.verticalHeader()
        vhead.setSectionResizeMode(QHeaderView.Fixed)
        vhead.setDefaultSectionSize(64)

        # шапка
        for i, value in enumerate(self._columns_):
            if i == 1:
                sz = 25
            elif i in self._money_cols_:
                sz = 140
            else:
                sz = 100

            item = QTableWidgetItem(value[1])
            item.setToolTip(value[2])
            self._grid.setHorizontalHeaderItem(i, item)
            self._grid.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed if i > 0 else QHeaderView.Stretch)
            self._grid.horizontalHeader().resizeSection(i, sz)

            if i in self._money_cols_:
                self._grid.setItemDelegateForColumn(i, GridMoneyItemDelegate(self._grid, bg_color=self._bg_colors_[i]))

        main_layout.addWidget(self._grid)
        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)
        btn_close.setFocus()

    def set_data(self, profiles: Profiles, robots, curr_uid=None):
        self._curr_uid = curr_uid
        row = 0
        self._grid.setSortingEnabled(False)
        self._grid.setRowCount(0)
        self._grid.setRowCount(len(profiles.profiles) + len(robots.keys()))

        for p in profiles.profiles:
            for col, value in enumerate(self._columns_):
                if col == 0:
                    icon = QIcon(Face2(p))
                    self.set_text_item(row, col, getattr(p, value[0]), icon, bold=curr_uid == p.uid, data=p.uid)
                elif col == 1:
                    self.set_bool_item(row, col, getattr(p, value[0]))
                else:
                    self.set_number_item(row, col, getattr(p, value[0]), bold=curr_uid == p.uid)
            row += 1

        for k, p in robots.items():
            for col, value in enumerate(self._columns_):
                if col == 0:
                    icon = QIcon(Avatar(name=k))
                    self.set_text_item(row, col, k, icon)
                elif col == 1:
                    self.set_bool_item(row, col, True)
                else:
                    self.set_number_item(row, col, p[value[0]])
            row += 1

        self._grid.setSortingEnabled(True)
        self._grid.sortByColumn(7, Qt.DescendingOrder)

    def set_item(self, row, col, item, bold=False):
        if col == 1:
            align = Qt.AlignCenter
        elif col > 1:
            align = Qt.AlignRight
        else:
            align = Qt.AlignLeft

        if bold:
            f = item.font()
            f.setBold(True)
            item.setFont(f)

        # item.setForeground(QColor(color))
        item.setBackground(QColor(self._bg_colors_[col]))
        item.setTextAlignment(align | Qt.AlignVCenter)
        self._grid.setItem(row, col, item)

    def set_text_item(self, row, col, value, icon=None, bold=False, data=None):
        if icon:
            item = QTableWidgetItem(icon, str(value))
        else:
            item = QTableWidgetItem(str(value))

        if data:
            item.setData(Qt.WhatsThisRole, data)

        self.set_item(row, col, item, bold=bold)

    def set_number_item(self, row, col, value, bold=False):
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, value)
        self.set_item(row, col, item, bold=bold)

    def set_bool_item(self, row, col, value):
        # item = QTableWidgetItem()
        # item.setFlags(Qt.ItemIsUserCheckable)
        # item.setCheckState(Qt.Checked if value else Qt.Unchecked)
        # self.set_item(row, col, item)
        cell_widget = QWidget()
        chb = QCheckBox()
        chb.setCheckState(Qt.Checked if value else Qt.Unchecked)
        chb.setEnabled(False)
        layout = QHBoxLayout(cell_widget)
        layout.addWidget(chb)
        layout.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        cell_widget.setLayout(layout)
        self._grid.setCellWidget(row, col, cell_widget)
