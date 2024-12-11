import random

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from core import const as eng_const
from models.params import Options
from gui.common.models import GameModel
from gui.common import const
from gui.common.client import GameServerClient
from gui.common.graphics import Face2
from gui.windows.agreements_dlg import AgreementsDialog


class CreateGameDialog(QDialog):

    def __init__(self, parent, game_id: int):
        super().__init__(parent)
        self._game_server_cli: GameServerClient = parent.game_server_cli
        self._agreements_dlg = AgreementsDialog(self, parent.options.as_dict())
        self._game: GameModel | None = None
        self._game_id = game_id
        self.players_box = None

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/app.ico'))
        self.setWindowTitle('Создать игру')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self._load_game()

    def init_ui(self):
        btn_ok = QPushButton(QIcon(f'{const.RES_DIR}/ok.png'), 'Создать')
        btn_ok.setDefault(True)
        btn_ok.setFixedWidth(140)
        btn_ok.clicked.connect(self._exec)
        btn_cancel = QPushButton(QIcon(f'{const.RES_DIR}/cancel.png'), 'Закрыть')
        btn_cancel.setFixedWidth(140)
        btn_cancel.clicked.connect(self.reject)
        buttons_box = QHBoxLayout()
        buttons_box.addWidget(btn_ok)
        buttons_box.addWidget(btn_cancel)

        main_layout = QVBoxLayout()

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(QLabel('Количество участников парии  '))
        sb = QSpinBox(self)
        sb.setMinimum(2)
        sb.setMaximum(3)
        sb.setFixedWidth(50)
        sb.setValue(self.get_agreements().players_cnt)
        sb.valueChanged.connect(self._count_change)
        layout.addWidget(sb)
        main_layout.addLayout(layout)

        group = QGroupBox('Игроки')
        self.players_box = QVBoxLayout()
        group.setLayout(self.players_box)
        main_layout.addLayout(self.players_box)

        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)

    def _count_change(self, value):
        if len(self._comboboxes) > value:
            QMessageBox.warning(self, 'В игре уже больше игроков, сначала надо выгнать кого-нибудь из игры')
            return

        self._players_cnt = value

    def _show_agreements(self):
        self._agreements_dlg.exec()

    def get_agreements(self):
        return Options(**self._agreements_dlg.get_agreements())

    def destroy(self, *args, **kwargs):
        self._agreements_dlg.destroy()
        super().destroy(*args, **kwargs)

    def _exec(self):
        self.accept()

    def _load_game(self):
        if not self._game_id:
            return
