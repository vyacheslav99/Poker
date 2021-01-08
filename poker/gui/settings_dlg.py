from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const
from modules.core import const as eng_const


class SettingsDialog(QDialog):

    def __init__(self, parent, params: dict):
        super().__init__(parent)
        self._params = params

        # элементы управления
        self._color_theme = None            # Цветовая тема
        self._deck_type = None              # Вид колоды
        self._back_type = None              # Вид рубашки
        self._sort_order = None             # Порядок сортировки карт на руках
        self._lear_order = None             # Порядок расположения мастей на руках
        self._start_type = None             # Вариант начала игры
        self._start_type_descr = None

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/settings.ico'))
        self.setWindowTitle('Настройки')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self.set_params()

    def init_ui(self):
        # Кнопки ОК, Отмена
        main_layout = QVBoxLayout()
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

        group = QGroupBox()
        layout = QGridLayout()
        layout.setHorizontalSpacing(20)

        # Вариант начала игры
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Вариант начала игры'))
        l2.addSpacing(10)
        self._start_type = QComboBox()
        self._start_type.setEditable(False)
        self._start_type.setFixedWidth(230)

        for descr in const.GAME_START_TYPES:
            self._start_type.addItem(f'{descr[0]}', QVariant(descr[1]))

        self._start_type.currentIndexChanged.connect(self._start_type_change)
        l2.addWidget(self._start_type)
        layout.addLayout(l2, 1, 1, Qt.AlignLeft)
        self._start_type_descr = QLabel('Выбери вариант')
        layout.addWidget(self._start_type_descr, 1, 2)

        # Тема оформления
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Тема оформления'))
        l2.addSpacing(35)
        self._color_theme = QComboBox()
        self._color_theme.setEditable(False)
        self._color_theme.setFixedWidth(100)

        for theme in const.COLOR_THEMES:
            self._color_theme.addItem(theme)

        l2.addWidget(self._color_theme)
        layout.addLayout(l2, 2, 1, Qt.AlignLeft)

        # Сортировка карт
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Сортировка карт'))
        l2.addSpacing(47)
        self._sort_order = QComboBox()
        self._sort_order.setEditable(False)
        self._sort_order.setFixedWidth(230)

        for i in range(2):
            self._sort_order.addItem('По возрастанию' if i == 0 else 'По убыванию')

        l2.addWidget(self._sort_order)
        layout.addLayout(l2, 3, 1, Qt.AlignLeft)

        # Порядок мастей
        l2 = QVBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Порядок расположения мастей<br>(перетаскивай масти для изменения)'))
        l2.addSpacing(5)
        self._lear_order = QListWidget()
        self._lear_order.setFlow(QListView.LeftToRight)
        self._lear_order.setGridSize(QSize(64, 32))
        self._lear_order.setMovement(QListView.Snap)
        self._lear_order.setFixedHeight(50)
        self._lear_order.setFixedWidth(300)
        self._lear_order.setDefaultDropAction(Qt.MoveAction)
        l2.addWidget(self._lear_order)
        layout.addLayout(l2, 4, 1, Qt.AlignLeft)

        # Выбор колоды
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Колода'))
        l2.addSpacing(20)
        self._deck_type = QComboBox()
        self._deck_type.setEditable(False)
        self._deck_type.setIconSize(QSize(64, 64))
        self._deck_type.setFixedWidth(230)

        for i, deck in enumerate(const.DECK_NAMES):
            px = QPixmap(f'{const.CARD_DECK_DIR}/{const.DECK_TYPE[i]}/qs.bmp')
            self._deck_type.addItem(QIcon(px), deck)

        l2.addWidget(self._deck_type)
        layout.addLayout(l2, 2, 2, Qt.AlignLeft)

        # Выбор рубашки
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Рубашка'))
        l2.addSpacing(10)
        self._back_type = QComboBox()
        self._back_type.setEditable(False)
        self._back_type.setIconSize(QSize(64, 64))
        self._back_type.setFixedWidth(230)

        for i in range(1, 10):
            px = QPixmap(f'{const.CARD_BACK_DIR}/back{i}.bmp')
            self._back_type.addItem(QIcon(px), f'Рубашка {i}')

        l2.addWidget(self._back_type)
        layout.addLayout(l2, 3, 2, Qt.AlignLeft)

        group.setLayout(layout)
        main_layout.addWidget(group)
        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)

    def set_params(self, params: dict=None):
        if params:
            self._params = params

        self._color_theme.setCurrentText(self._params.get('color_theme', 'green'))
        self._deck_type.setCurrentIndex(const.DECK_TYPE.index(self._params.get('deck_type', 'eng')))
        self._back_type.setCurrentIndex(self._params.get('back_type', 1) - 1)
        self._sort_order.setCurrentIndex(self._params.get('sort_order', 1))
        self._start_type.setCurrentIndex(self._params.get('start_type', 3))

        self._lear_order.clear()
        for lear in self._params.get('lear_order', []):
            px = QPixmap(f'{const.SUITS_DIR}/{const.LEARS[lear]}.png')
            item = QListWidgetItem(QIcon(px), '')
            item.setData(Qt.DisplayRole, QVariant((lear,)))
            self._lear_order.addItem(item)

    def get_params(self):
        self._params['color_theme'] = self._color_theme.currentText()
        self._params['deck_type'] = const.DECK_TYPE[self._deck_type.currentIndex()]
        self._params['back_type'] = self._back_type.currentIndex() + 1
        self._params['sort_order'] = self._sort_order.currentIndex()
        self._params['start_type'] = self._start_type.currentIndex()

        self._params['lear_order'] = []
        for i in range(self._lear_order.count()):
            self._params['lear_order'].append(self._lear_order.item(i).data(Qt.DisplayRole)[0])

        return self._params

    def _start_type_change(self):
        self._start_type_descr.setText(self._start_type.currentData())
