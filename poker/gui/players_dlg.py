import random
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const
from modules.core import const as core_const
from modules.core import helpers


class PlayersDialog(QDialog):

    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self._players = kwargs.get('players', [])
        self.setWindowIcon(QIcon(f'{const.RES_DIR}/player.ico'))
        self.setWindowTitle('Участники игры')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self.resize(800, 600)

    def init_ui(self):
        btn_ok = QPushButton("OK")
        btn_ok.setDefault(True)
        btn_ok.setFixedWidth(140)
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setFixedWidth(140)
        btn_cancel.clicked.connect(self.reject)
        buttonsBox = QHBoxLayout()
        buttonsBox.addWidget(btn_ok)
        buttonsBox.addWidget(btn_cancel)

        mainLayout = QVBoxLayout()

        for p in self._players:
            pb = QHBoxLayout()
            pb.setAlignment(Qt.AlignLeft)

            mainLayout.addLayout(pb)

        mainLayout.addLayout(buttonsBox)
        self.setLayout(mainLayout)

    @property
    def players(self):
        return self._players
