from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const


class GameTableDialog(QDialog):

    users_color = ('Yellow', 'GreenYellow', 'Silver', 'Aqua')
    users_bg = ('DarkGreen', 'MidnightBlue', 'DarkRed', 'DarkSlateGray')

    def __init__(self, players, parent=None):
        super().__init__(parent)

        self.players = players
        self.game_table = None

        self.setWindowTitle('Запись хода игры')
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        pal = QPalette()
        pal.setBrush(QPalette.Window, QBrush(QPixmap(f'{const.BG_DIR}/default.bmp')))
        self.setPalette(pal)

        self.btn = QPushButton("Продолжить")
        self.btn.setFixedHeight(50)
        f = self.btn.font()
        f.setWeight(65)
        f.setPointSize(12)
        self.btn.setFont(f)
        # self.btn.setStyleSheet('QPushButton {background-color: LightCyan; color: Purple}')
        self.btn.setStyleSheet('QPushButton {background-color: YellowGreen; color: DarkBlue}')
        self.btn.clicked.connect(self.close)

        # table
        self.table = QTableWidget(self)
        self.table.setStyleSheet('QTableWidget {background-color: Green}')
        self.table.setColumnCount(len(self.players) * 4 + 1)
        self.table.setRowCount(2)
        self.table.setItem(0, 0, QTableWidgetItem(' '))

        i = 1
        for p in self.players:
            n = i + 3
            self.table.setItem(0, i, QTableWidgetItem(p.name))
            self.table.setSpan(0, i, 1, 4)
            i = n + 1

        self.table.setItem(1, 0, QTableWidgetItem('Кон'))

        for i, cap in enumerate(['Заказ', 'Взял', 'Очки', 'Счет'] * len(self.players), 1):
            self.table.setItem(1, i, QTableWidgetItem(cap))

        self.set_column_style(0, 0, 1, Qt.AlignHCenter, 'Purple', 'YellowGreen', 13, 75)
        self.table.item(0, 0).setBackground(QColor('Green'))

        j = 1
        for i in range(len(self.players)):
            for _ in range(4):
                self.set_column_style(j, 0, 1, Qt.AlignHCenter, self.users_color[i], self.users_bg[i], 13, 75)
                j += 1

        # self.table.resizeColumnsToContents()  # автоподбор ширины колонок по содержимому
        # автоподгон ширины колонок по ширине таблицы
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # запрет на редактирование ячеек
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)

        self.form = QFormLayout()
        self.form.addRow(self.table)
        self.form.addRow(self.btn)

        self.setLayout(self.form)
        self.setFixedSize(*const.WINDOW_SIZE)
        self.resize(*const.WINDOW_SIZE)

    def set_column_style(self, col, start, stop, alignment, color, bg_color, font_size, font_weight):
        """
        Задает оформление ячейкам колонки таблицы в заданном диапазоне строк

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
            item = self.table.item(row, col)
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

        self.set_column_style(0, r, r, Qt.AlignHCenter, colors[0], 'YellowGreen', 13, 70)

        j = 1
        for i in range(len(self.players)):
            for x in range(4):
                self.set_column_style(j, r, r, Qt.AlignHCenter, colors[j], self.users_bg[i], 13, 70)
                j += 1

        # self.table.resizeColumnsToContents()
        self.table.verticalScrollBar().setSliderPosition(r)
