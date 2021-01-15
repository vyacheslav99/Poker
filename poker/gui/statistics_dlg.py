import os
import shutil
import string

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const
from gui.graphics import Face2
from modules.params import Profiles


class StatisticsDialog(QDialog):

    def __init__(self, parent, profiles: Profiles):
        super().__init__(parent)
        self._profiles = profiles

        # элементы управления
        self._grid = None

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/player.ico'))
        self.setWindowTitle('Статистика игроков')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

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

        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)
