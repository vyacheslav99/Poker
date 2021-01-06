import random
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from modules.core import helpers
from gui import const
from gui.graphics import Face2


class PlayersDialog(QDialog):

    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self._players_cnt = kwargs.get('players_cnt', 2)
        self._cb_items = []
        self._comboboxes = []

        robots = sorted([r for r in const.ROBOTS])
        for i, rob in enumerate(robots):
            self._cb_items.append(helpers.Player())
            self._cb_items[i].uid = i
            self._cb_items[i].is_robot = True
            self._cb_items[i].name = rob
            self._cb_items[i].risk_level = random.randint(0, 2)

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/player.ico'))
        self.setWindowTitle('Участники игры')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        # self.resize(800, 600)
        # self.setFixedWidth(400)

    def init_ui(self):
        btn_ok = QPushButton("OK")
        btn_ok.setDefault(True)
        btn_ok.setFixedWidth(140)
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setFixedWidth(140)
        btn_cancel.clicked.connect(self.reject)
        buttons_box = QHBoxLayout()
        buttons_box.addWidget(btn_ok)
        buttons_box.addWidget(btn_cancel)

        players_box = QHBoxLayout()
        players_box.addWidget(QLabel('Количество участников парии (кроме вас)'))
        sb = QSpinBox()
        sb.setMinimum(2)
        sb.setMaximum(3)
        sb.setValue(self._players_cnt)
        sb.valueChanged.connect(self._count_change)
        players_box.addWidget(sb)

        main_layout = QVBoxLayout()
        main_layout.addLayout(players_box)
        selected = set()

        for i in range(3):
            pb = QHBoxLayout()
            pb.setAlignment(Qt.AlignLeft)
            lb = QLabel()
            lb.setText(f'Игрок {i + 1}')

            cb = QComboBox()
            cb.setEditable(False)
            cb.setIconSize(QSize(64, 64))
            cb.setFixedWidth(250)
            cb.setEnabled(i < self._players_cnt)

            for el in self._cb_items:
                cb.addItem(QIcon(Face2(el)), f'    {el.name}', QVariant(el))

            i = random.randrange(0, len(self._cb_items))
            while i in selected:
                i = random.randrange(0, len(self._cb_items))
            selected.add(i)
            cb.setCurrentIndex(i)
            self._comboboxes.append(cb)

            pb.addWidget(lb)
            pb.addWidget(cb)
            main_layout.addLayout(pb)

        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)

    def _count_change(self, value):
        self._players_cnt = value
        self._comboboxes[-1].setEnabled(len(self._comboboxes) <= self._players_cnt)

    def get_players(self):
        players = []

        for i in range(self._players_cnt):
            players.append(self._comboboxes[i].currentData())

        return players
