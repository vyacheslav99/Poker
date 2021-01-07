import random
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from modules.core import helpers, const as eng_const
from gui import const
from gui.graphics import Face2


class PlayersDialog(QDialog):

    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self._players_cnt = kwargs.get('players_cnt', 2)
        self._cb_items = []
        self._comboboxes = []
        self._radiogroups = []

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
        btn_ok = QPushButton(QIcon(f'{const.RES_DIR}/ok.png'), 'OK')
        btn_ok.setDefault(True)
        btn_ok.setFixedWidth(140)
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton(QIcon(f'{const.RES_DIR}/cancel.png'), 'Отмена')
        btn_cancel.setFixedWidth(140)
        btn_cancel.clicked.connect(self.reject)
        buttons_box = QHBoxLayout()
        buttons_box.addWidget(btn_ok)
        buttons_box.addWidget(btn_cancel)

        players_box = QHBoxLayout()
        players_box.setAlignment(Qt.AlignLeft)
        players_box.addWidget(QLabel('Количество участников парии (кроме вас)  '))
        sb = QSpinBox()
        sb.setMinimum(2)
        sb.setMaximum(3)
        sb.setFixedWidth(50)
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
            lb.setText(f'Игрок {i + 1}  ')

            cb = QComboBox()
            cb.setEditable(False)
            cb.setIconSize(QSize(64, 64))
            cb.setFixedWidth(230)
            cb.setEnabled(i < self._players_cnt)

            for el in self._cb_items:
                cb.addItem(QIcon(Face2(el)), f'    {el.name}', QVariant(el))

            x = random.randrange(0, len(self._cb_items))
            while x in selected:
                x = random.randrange(0, len(self._cb_items))
            selected.add(x)
            cb.setCurrentIndex(x)
            cb.currentIndexChanged.connect(self._combo_change)
            self._comboboxes.append(cb)

            gb = QGroupBox()
            l = QHBoxLayout()
            bg = QButtonGroup()
            bg.setExclusive(True)
            for n in range(3):
                rbtn = QRadioButton(eng_const.RISK_LVL_NAMES[n])
                rbtn.setEnabled(i < self._players_cnt)
                bg.addButton(rbtn, id=n)
                l.addWidget(rbtn)

            bg.buttons()[self._cb_items[x].risk_level].setChecked(True)
            self._radiogroups.append(bg)

            gb.setLayout(l)
            pb.addWidget(lb)
            pb.addWidget(cb)
            pb.addWidget(gb)
            main_layout.addLayout(pb)

        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)

    def _count_change(self, value):
        self._players_cnt = value
        self._comboboxes[-1].setEnabled(len(self._comboboxes) <= self._players_cnt)

        for btn in self._radiogroups[-1].buttons():
            btn.setEnabled(len(self._comboboxes) <= self._players_cnt)

    def _combo_change(self, index):
        # т.к. мы тут не знаем, какой именно комбобокс вызвал  событие - просто переберем все
        for i, cb in enumerate(self._comboboxes):
            self._radiogroups[i].buttons()[cb.currentData().risk_level].setChecked(True)

    def get_players(self):
        players = []

        for i in range(self._players_cnt):
            p = self._comboboxes[i].currentData()
            p.risk_level = self._radiogroups[i].checkedId()
            players.append(self._comboboxes[i].currentData())

        return players
