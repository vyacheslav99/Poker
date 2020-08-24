from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const


class DebugInfoDialog(QDialog):

    def __init__(self, players, parent=None):
        super().__init__(parent)

        self.players = players

        self.setWindowTitle('Отладочная информация')
        self.setModal(False)
        self.setWindowFlags(self.windowFlags() & Qt.Tool & ~Qt.WindowContextHelpButtonHint)

        self.form = QFormLayout()
        self.form.addRow(self.header)
        self.form.addRow(self.table)
        self.form.addRow(self.btn)

        self.setLayout(self.form)
        # self.setFixedSize(*const.WINDOW_SIZE)
        # self.resize(*const.WINDOW_SIZE)

    def show_players(self):
        pass
