import os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const, client
from core import const as eng_const
from models.params import Profiles


class SettingsDialog(QDialog):

    def __init__(self, parent, params: dict, profiles: Profiles):
        super().__init__(parent)
        self._params = params
        self._profiles = profiles

        # элементы управления
        self._deck_type = None              # Вид колоды
        self._back_type = None              # Вид рубашки
        self._sort_order = None             # Порядок сортировки карт на руках
        self._lear_order = None             # Порядок расположения мастей на руках
        self._start_type = None             # Вариант начала игры
        self._current_profile = None        # Смена текущего профиля
        self._server = None                 # Адрес сервера
        self._server_info = None            # Текст с информацией о состоянии подключения
        self._btn_connect = None            # кнопка Проверить подключение
        self._color_theme = None            # Цветовая тема
        self._style = None                  # Графический стиль
        self._show_bikes = None             # Травить байки

        for attr in const.DECORATION_THEMES['green'].keys():
            setattr(self, f'_{attr}', None)

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/settings.ico'))
        self.setWindowTitle('Настройки')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self.set_params()

    def init_ui(self):
        # Кнопки ОК, Отмена, Сброс
        main_layout = QVBoxLayout()
        btn_ok = QPushButton(QIcon(f'{const.RES_DIR}/ok.png'), 'OK')
        btn_ok.setDefault(True)
        btn_ok.setFixedWidth(140)
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton(QIcon(f'{const.RES_DIR}/cancel.png'), 'Отмена')
        btn_cancel.setFixedWidth(140)
        btn_cancel.clicked.connect(self.reject)
        btn_reset = QPushButton('Сброс настроек')
        btn_reset.setFixedWidth(150)
        btn_reset.clicked.connect(self.reset)

        buttons_box = QHBoxLayout()
        buttons_box.addWidget(btn_reset, alignment=Qt.AlignLeft)
        buttons_box.addWidget(btn_ok, 1, alignment=Qt.AlignRight)
        buttons_box.addWidget(btn_cancel, alignment=Qt.AlignRight)
        btn_ok.setFocus()

        group = QGroupBox()
        layout = QGridLayout()
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(20)

        # Текущий профиль
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Текущий профиль'))
        l2.addSpacing(30)
        self._current_profile = QComboBox()
        self._current_profile.setEditable(False)
        self._current_profile.setFixedWidth(230)

        for p in self._profiles.profiles:
            self._current_profile.addItem(p.name, QVariant(p.uid))

        l2.addWidget(self._current_profile)
        layout.addLayout(l2, 1, 1, Qt.AlignLeft)

        # Cервер
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Сервер'))
        self._server = QLineEdit()

        l2.addWidget(self._server)
        layout.addLayout(l2, 1, 2, alignment=Qt.AlignRight)

        l2 = QHBoxLayout()
        self._btn_connect = QPushButton('Проверить подключение')
        # btn_connect.setFixedWidth(150)
        self._btn_connect.clicked.connect(self.check_connection)
        self._server_info = QLabel('Состояние: неизвестно')
        self._server_info.setStyleSheet('QLabel {color: gray}')
        l2.addWidget(self._btn_connect)
        l2.addWidget(self._server_info)
        layout.addLayout(l2, 2, 2, alignment=Qt.AlignLeft)

        # Вариант начала игры
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Вариант начала игры'))
        l2.addSpacing(12)
        self._start_type = QComboBox()
        self._start_type.setEditable(False)
        self._start_type.setFixedWidth(230)

        for descr in const.GAME_START_TYPES:
            self._start_type.addItem(f'{descr[0]}', QVariant(descr[1]))

        l2.addWidget(self._start_type)
        layout.addLayout(l2, 2, 1, Qt.AlignLeft)

        # Выбор колоды
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Колода'))
        l2.addSpacing(95)
        self._deck_type = QComboBox()
        self._deck_type.setEditable(False)
        self._deck_type.setIconSize(QSize(64, 64))
        self._deck_type.setFixedWidth(230)

        for i, deck in enumerate(const.DECK_NAMES):
            px = QPixmap(f'{const.CARD_DECK_DIR}/{const.DECK_TYPE[i]}/qs.bmp')
            self._deck_type.addItem(QIcon(px), deck)

        l2.addWidget(self._deck_type)
        layout.addLayout(l2, 3, 1, Qt.AlignLeft)

        # Выбор рубашки
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Рубашка'))
        # l2.addSpacing(10)
        self._back_type = QComboBox()
        self._back_type.setEditable(False)
        self._back_type.setIconSize(QSize(64, 64))
        self._back_type.setFixedWidth(230)

        for i in range(1, 10):
            px = QPixmap(f'{const.CARD_BACK_DIR}/back{i}.bmp')
            self._back_type.addItem(QIcon(px), f'Рубашка {i}')

        l2.addWidget(self._back_type)
        layout.addLayout(l2, 3, 2, Qt.AlignRight)

        # Сортировка карт
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Сортировка карт'))
        l2.addSpacing(37)
        self._sort_order = QComboBox()
        self._sort_order.setEditable(False)
        self._sort_order.setFixedWidth(230)

        for i in range(2):
            self._sort_order.addItem('По возрастанию' if i == 0 else 'По убыванию')

        l2.addWidget(self._sort_order)
        layout.addLayout(l2, 4, 1, Qt.AlignLeft)

        # Порядок мастей
        l2 = QVBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        # l2.addWidget(QLabel('Порядок расположения мастей'))
        # l2.addSpacing(5)
        self._lear_order = QListWidget()
        self._lear_order.setFlow(QListView.LeftToRight)
        self._lear_order.setGridSize(QSize(64, 32))
        self._lear_order.setMovement(QListView.Snap)
        self._lear_order.setFixedHeight(40)
        self._lear_order.setFixedWidth(300)
        self._lear_order.setDefaultDropAction(Qt.MoveAction)
        self._lear_order.setToolTip('Порядок расположения мастей\nЧтобы изменить порядок, перетащи масть мышкой в нужное место')
        l2.addWidget(self._lear_order)
        layout.addLayout(l2, 4, 2, Qt.AlignRight)

        # Травить байки
        l2 = QHBoxLayout()
        self._show_bikes = QCheckBox('Травить байки во время игры')
        l2.addWidget(self._show_bikes)
        layout.addLayout(l2, 5, 1, Qt.AlignLeft)

        group.setLayout(layout)
        main_layout.addWidget(group)

        # Группа Оформление
        group = QGroupBox('Оформление')
        layout = QGridLayout()
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        # Тема оформления
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Тема оформления'))
        l2.addSpacing(10)
        self._color_theme = QComboBox()
        self._color_theme.setEditable(False)
        self._color_theme.setFixedWidth(120)

        for theme in const.DECORATION_THEMES.keys():
            self._color_theme.addItem(theme)

        self._color_theme.currentIndexChanged.connect(self.color_theme_change)
        l2.addWidget(self._color_theme)
        layout.addLayout(l2, 1, 1, alignment=Qt.AlignLeft)

        # Стиль
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Стиль'))
        l2.addSpacing(10)
        self._style = QComboBox()
        self._style.setEditable(False)
        self._style.setFixedWidth(120)

        for style in QStyleFactory.keys():
            self._style.addItem(style)

        l2.addWidget(self._style)
        layout.addLayout(l2, 1, 3, alignment=Qt.AlignRight)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, 2, 1, 2, 3)

        row = 4
        col = 1
        for i, attr_name in enumerate(const.DECORATION_THEMES['green'].keys()):
            l2 = QHBoxLayout()
            lb = QLabel(const.THEME_CONTROLS_TITLE[attr_name])
            lb.setAlignment(Qt.AlignRight)
            l2.addWidget(lb, alignment=Qt.AlignRight | Qt.AlignVCenter)
            # l2.addSpacing(10)
            attr = QComboBox()
            attr.setEditable(False)
            attr.setIconSize(QSize(16, 16))
            attr.setFixedWidth(120)
            setattr(self, f'_{attr_name}', attr)

            if attr_name == const.BG_TEXTURE:
                attr.addItem(const.BG_TEXTURE_NOTHING)
                for fn in os.listdir(const.BG_DIR):
                    px = QPixmap(f'{const.BG_DIR}/{fn}')
                    attr.addItem(QIcon(px), fn)
            else:
                for color in const.COLORS:
                    px = QPixmap(f'{const.SUITS_DIR}/c.png')
                    px.fill(QColor(color))
                    attr.addItem(QIcon(px), color)

            l2.addWidget(attr)
            layout.addLayout(l2, row, col)

            col += 1
            if col > 3 or i == 1:
                row += 1
                col = 1

        group.setLayout(layout)
        main_layout.addSpacing(5)
        main_layout.addWidget(group)
        main_layout.addSpacing(10)
        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)

    def allow_profile_change(self, allowed):
        self._current_profile.setEnabled(allowed)

    def set_params(self, params: dict=None):
        if params:
            self._params = params

        self._server.setText(self._params.get('server', ''))
        self._deck_type.setCurrentIndex(const.DECK_TYPE.index(self._params.get('deck_type', 'eng')))
        self._back_type.setCurrentIndex(self._params.get('back_type', 1) - 1)
        self._sort_order.setCurrentIndex(self._params.get('sort_order', 0))
        self._start_type.setCurrentIndex(self._params.get('start_type', const.GAME_START_TYPE_ALL))
        self._color_theme.setCurrentText(self._params.get('color_theme', 'green'))
        self._style.setCurrentText(self._params.get('style', 'Fusion'))
        self._show_bikes.setChecked(self._params.get('show_bikes', True))

        if self._params['color_theme'] == 'green':
            self.color_theme_change(0)

        if self._profiles.count():
            self._current_profile.setCurrentIndex(self._profiles.get_item(self._params.get('user'))[0])

        self._lear_order.clear()
        for lear in self._params.get('lear_order', []):
            px = QPixmap(f'{const.SUITS_DIR}/{const.LEARS[lear]}.png')
            item = QListWidgetItem(QIcon(px), '')
            item.setData(Qt.DisplayRole, QVariant((lear,)))
            self._lear_order.addItem(item)

    def get_params(self):
        self._params['server'] = self._server.text() or None
        self._params['deck_type'] = const.DECK_TYPE[self._deck_type.currentIndex()]
        self._params['back_type'] = self._back_type.currentIndex() + 1
        self._params['sort_order'] = self._sort_order.currentIndex()
        self._params['start_type'] = self._start_type.currentIndex()
        self._params['user'] = self._current_profile.currentData()
        self._params['color_theme'] = self._color_theme.currentText()
        self._params['style'] = self._style.currentText()
        self._params['show_bikes'] = self._show_bikes.isChecked()

        self._params['lear_order'] = []
        for i in range(self._lear_order.count()):
            self._params['lear_order'].append(self._lear_order.item(i).data(Qt.DisplayRole)[0])

        if self._params['color_theme'] == 'custom':
            for k in self._params['custom_decoration'].keys():
                attr = getattr(self, f'_{k}')
                if k == const.BG_TEXTURE:
                    if attr.currentText() == const.BG_TEXTURE_NOTHING:
                        self._params['custom_decoration'][k] = None
                    else:
                        self._params['custom_decoration'][k] = f'{const.BG_DIR}/{attr.currentText()}'
                else:
                    self._params['custom_decoration'][k] = attr.currentText()

        return self._params

    def reset(self):
        res = QMessageBox.question(self, 'Подтверждение', 'Действительно сбросить настройки до стандартных?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res != QMessageBox.Yes:
            return

        self._server.setText('')
        self._deck_type.setCurrentIndex(0)
        self._back_type.setCurrentIndex(0)
        self._sort_order.setCurrentIndex(0)
        self._start_type.setCurrentIndex(const.GAME_START_TYPE_ALL)
        self._color_theme.setCurrentText('green')
        self._style.setCurrentText('Fusion')
        self._show_bikes.setChecked(True)

        self._lear_order.clear()
        for lear in (eng_const.LEAR_SPADES, eng_const.LEAR_CLUBS, eng_const.LEAR_DIAMONDS, eng_const.LEAR_HEARTS):
            px = QPixmap(f'{const.SUITS_DIR}/{const.LEARS[lear]}.png')
            item = QListWidgetItem(QIcon(px), '')
            item.setData(Qt.DisplayRole, QVariant((lear,)))
            self._lear_order.addItem(item)

    def color_theme_change(self, index):
        theme = self._color_theme.currentText()

        if theme == 'custom':
            params = self._params['custom_decoration']
            enabled = True
        else:
            params = const.DECORATION_THEMES[theme]
            enabled = False

        for k, v in params.items():
            attr = getattr(self, f'_{k}')
            attr.setEnabled(enabled)
            if k == const.BG_TEXTURE:
                if v is None:
                    attr.setCurrentText(const.BG_TEXTURE_NOTHING)
                else:
                    attr.setCurrentText(v.split('/')[-1])
            else:
                attr.setCurrentText(v.lower())

    def check_connection(self):
        color = 'gray'

        if self._server.text().strip():
            self._btn_connect.setEnabled(False)
            self._server_info.setText('Минуточку...')

            res, mes = client.Client(self._server.text().strip()).is_alive()
            if res:
                text = 'OK'
                color = 'green'
            else:
                text = 'N/A'
                color = 'maroon'

            mes = ': '.join(['OK' if res else 'N/A', mes])
            self._server_info.setText(f'Состояние: {text}')

            if not res:
                QMessageBox.warning(self, 'Ошибка', mes)

            self._btn_connect.setEnabled(True)
        else:
            self._server_info.setText('не задан хост')

        self._server_info.setStyleSheet(''.join(('QLabel {color:', color, '}')))