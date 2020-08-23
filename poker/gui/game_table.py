from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const


class GameTableDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Табилца игры')
        self.setModal(True)

        self.btn = QPushButton("Закрыть")
        self.btn.setFixedHeight(50)
        f = self.btn.font()
        f.setWeight(65)
        f.setPointSize(12)
        self.btn.setFont(f)
        self.btn.setStyleSheet('QPushButton {background-color: LightCyan; color: Purple}')
        self.btn.clicked.connect(self.close)

        table = QTableWidget(self)  # Создаём таблицу
        table.setColumnCount(3)     # Устанавливаем три колонки
        table.setRowCount(1)        # и одну строку в таблице

        # Устанавливаем заголовки таблицы
        table.setHorizontalHeaderLabels(["Header 1", "Header 2", "Header 3"])

        # Устанавливаем всплывающие подсказки на заголовки
        table.horizontalHeaderItem(0).setToolTip("Column 1 ")
        table.horizontalHeaderItem(1).setToolTip("Column 2 ")
        table.horizontalHeaderItem(2).setToolTip("Column 3 ")

        # Устанавливаем выравнивание на заголовки
        table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
        table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
        table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignRight)

        # заполняем первую строку
        table.setItem(0, 0, QTableWidgetItem("Text in column 1"))
        table.setItem(0, 1, QTableWidgetItem("Text in column 2"))
        table.setItem(0, 2, QTableWidgetItem("Text in column 3"))

        # делаем ресайз колонок по содержимому
        table.resizeColumnsToContents()

        self.form = QFormLayout()
        # self.form.setSpacing(20)
        self.form.addRow(self.btn)

        self.setLayout(self.form)
        self.setFixedSize(*const.WINDOW_SIZE)
        self.resize(*const.WINDOW_SIZE)
