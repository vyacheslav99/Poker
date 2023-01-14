from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from domain.models.params import Params
from gui import const


class GameTableDialog(QDialog):

    def __init__(self, players, parent):
        super().__init__(parent)

        self.players = players
        self.params: Params = parent.params
        self.game_table = None

        self.users_color = (self.params.color_player_1(), self.params.color_player_2(), self.params.color_player_3(),
                            self.params.color_player_4())
        self.users_bg = (self.params.bg_player_1(), self.params.bg_player_2(), self.params.bg_player_3(),
                         self.params.bg_player_4())

        self.setWindowTitle('Запись хода игры')
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        if self.params.bg_texture():
            bg = QPixmap(self.params.bg_texture())
        else:
            bg = QColor(self.params.bg_color())

        pal = QPalette()
        pal.setBrush(QPalette.Window, QBrush(bg))
        self.setPalette(pal)

        self.btn = QPushButton("Продолжить")
        self.btn.setFixedHeight(50)
        f = self.btn.font()
        f.setWeight(65)
        f.setPointSize(12)
        self.btn.setFont(f)
        self.btn.setStyleSheet('QPushButton {background-color: %s; color: %s}' %
                               (self.params.bg_buttons_2(), self.params.color_buttons_2()))
        self.btn.clicked.connect(self.close)

        # table
        self.header = QTableWidget(self)
        self.header.setStyleSheet('QTableWidget {background-color: %s}' % self.params.bg_color())
        self.header.setColumnCount(len(self.players) * 4 + 1)
        self.header.setRowCount(2)
        self.header.setItem(0, 0, QTableWidgetItem(' '))

        i = 1
        for p in self.players:
            n = i + 3
            self.header.setItem(0, i, QTableWidgetItem(p.name))
            self.header.setSpan(0, i, 1, 4)
            i = n + 1

        self.header.setItem(1, 0, QTableWidgetItem('Кон'))

        for i, cap in enumerate(['Заказ', 'Взял', 'Очки', 'Счет'] * len(self.players), 1):
            self.header.setItem(1, i, QTableWidgetItem(cap))

        self.set_column_style(self.header, 0, 0, 1, Qt.AlignHCenter, self.params.color_buttons_2(),
                              self.params.bg_buttons_2(), 13, 75)
        self.header.item(0, 0).setBackground(QColor(self.params.bg_color()))

        j = 1
        for i in range(len(self.players)):
            for _ in range(4):
                self.set_column_style(self.header, j, 0, 1, Qt.AlignHCenter, self.users_color[i], self.users_bg[i], 13, 75)
                j += 1

        # автоподбор ширины колонок по содержимому
        # self.table.resizeColumnsToContents()
        # автоподгон ширины колонок по ширине таблицы
        self.header.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # запрет на редактирование ячеек
        self.header.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.header.verticalHeader().setVisible(False)
        self.header.horizontalHeader().setVisible(False)
        self.header.setFixedHeight(76)

        self.table = QTableWidget(self)
        self.table.setStyleSheet('QTableWidget {background-color: %s}' % self.params.bg_color())
        self.table.setColumnCount(len(self.players) * 4 + 1)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)

        self.form = QFormLayout()
        self.form.addRow(self.header)
        self.form.addRow(self.table)
        self.form.addRow(self.btn)

        self.setLayout(self.form)
        self.setFixedSize(*const.WINDOW_SIZE)
        self.resize(*const.WINDOW_SIZE)

    def set_column_style(self, table, col, start, stop, alignment, color, bg_color, font_size, font_weight):
        """
        Задает оформление ячейкам колонки таблицы в заданном диапазоне строк

        :param table: таблица, к которой применяем стиль
        :param int col: индекс колонки
        :param int start: индекс строки, с которой начать, включительно
        :param int stop: индекс строки, которой закончить, включительно
        :param alignment: выравнивание
        :param str color: цвет текста
        :param str bg_color: цвет фона ячейки
        :param int font_size: размер шрифта
        :param int font_weight: жирность шрифта
        """

        for row in range(start, stop + 1):
            item = table.item(row, col)
            if item:
                item.setTextAlignment(alignment)  # Qt.AlignHCenter
                item.setForeground(QColor(color))
                item.setBackground(QColor(bg_color))
                f = item.font()
                f.setWeight(font_weight)
                f.setPointSize(font_size)
                item.setFont(f)

    def add_row(self, row, colors):
        """
        Добавить строку к таблице

        :param list row: список значений ячеек от первой колонки до последней
        :param dict colors: цвета текста
        """

        self.table.setRowCount(self.table.rowCount() + 1)
        r = self.table.rowCount() - 1

        for i, s in enumerate(row):
            item = QTableWidgetItem(f'{s}')
            item.setToolTip(item.text())
            self.table.setItem(r, i, item)

        self.set_column_style(self.table, 0, r, r, Qt.AlignHCenter, colors[0], self.params.bg_buttons_2(), 13, 70)

        j = 1
        for i in range(len(self.players)):
            for x in range(4):
                self.set_column_style(self.table, j, r, r, Qt.AlignHCenter, colors[j], self.users_bg[i], 13, 70)
                j += 1

        # self.table.resizeColumnsToContents()
        # self.table.verticalScrollBar().setSliderPosition(r)
        self.table.scrollToBottom()
