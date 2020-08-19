import os
import random

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import utils, const
from game import engine, helpers, const as eng_const

# print(QStyleFactory.keys())


class QCard(QGraphicsPixmapItem):

    def __init__(self, app, card, player, deck, back, removable=True, tooltip=None, replace_tooltip=False):
        super(QCard, self).__init__()

        self.app = app
        self.card = card
        self.player = player
        self.deck = deck
        self.back = back
        self.removable = removable
        self._tooltip = tooltip
        self.replace_tooltip = replace_tooltip
        self.side = None

        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(const.CARD_BASE_Z_VALUE)
        self.set_std_shadow()

        self.back = QPixmap(f'{const.CARD_BACK_DIR}/{self.back}.bmp')
        if card.joker:
            self.face = QPixmap(f'{const.CARD_DECK_DIR}/{self.deck}/j.bmp')
        else:
            self.face = QPixmap(f'{const.CARD_DECK_DIR}/{self.deck}/{const.CARDS[self.card.value]}{const.LEARS[self.card.lear]}.bmp')

    def turn_face_up(self):
        self.side = const.CARD_SIDE_FACE
        self.setPixmap(self.face)
        self.set_tooltip()

        if self.player:
            self.setCursor(Qt.PointingHandCursor)

    def turn_back_up(self):
        self.side = const.CARD_SIDE_BACK
        self.setPixmap(self.back)
        self.setCursor(Qt.ArrowCursor)
        # todo: После тестирования убрать показ тултипа когда рубашка вверх
        self.set_tooltip()
        # self.setToolTip('')

    def is_face_up(self):
        return self.side == const.CARD_SIDE_FACE

    def set_tooltip(self):
        if self.replace_tooltip and self._tooltip:
            val = self._tooltip
        else:
            c = 'red' if self.card.lear > 1 else 'navy'
            val = f'{eng_const.CARD_NAMES[self.card.value]} <span style="color:{c}">{eng_const.LEAR_SYMBOLS[self.card.lear]}</span>'
            if self.card.joker:
                val = f'Джокер ({val})'
            if self._tooltip:
                val = f'{self._tooltip} {val}'

        self.setToolTip(val)

    def set_color_shadow(self):
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(30)
        sh.setOffset(5)
        sh.setColor(Qt.green)
        self.setGraphicsEffect(sh)

    def set_std_shadow(self):
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(50)
        self.setGraphicsEffect(sh)

    def mousePressEvent(self, e):
        if self.player and self.is_face_up():
            self.app.card_click(self)

        super(QCard, self).mousePressEvent(e)


class Face(QGraphicsPixmapItem):

    def __init__(self, player, *args):
        super(Face, self).__init__(*args)
        self.player = player
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player):
        self._player = player

        if os.path.exists(f'{const.FACE_DIR}/{self._player.name}.bmp'):
            self.setPixmap(QPixmap(f'{const.FACE_DIR}/{self._player.name}.bmp'))
        else:
            self.setPixmap(QPixmap(f'{const.FACE_DIR}/user.jpg'))


class Lear(QGraphicsPixmapItem):

    def __init__(self, lear, *args):
        super(Lear, self).__init__(*args)
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        if lear == eng_const.LEAR_NOTHING:
            self.setPixmap(QPixmap(f'{const.SUITS_DIR}/none.ico'))
            self.setToolTip('Козырь: нет')
        else:
            self.setPixmap(QPixmap(f'{const.SUITS_DIR}/{const.LEARS[lear]}.ico'))
            self.setToolTip(f'Козырь: {eng_const.LEAR_NAMES[lear]}')

class Area(QGraphicsRectItem):

    def __init__(self, parent, size, *args):
        super(Area, self).__init__(*args)
        self.parent = parent
        self.setRect(QRectF(0, 0, size[0], size[1]))
        color = QColor(Qt.black)
        color.setAlpha(50)
        brush = QBrush(color)
        self.setBrush(brush)
        self.setPen(QPen(Qt.black))
        self.setZValue(-1)


class MainWnd(QMainWindow):

    def __init__(self, app):
        super().__init__()

        self.options = {}
        self.players = []
        self.buttons = []
        self.labels = []
        self.table = {}
        self.bet = None
        self.game = None
        self.is_new_round = False
        self.deck_type = None
        self.back_type = None
        self.order_dark = None
        self.table_label = None
        self.next_button = None
        self.deal_label = None
        self.first_move_label = None
        self.order_info_label = None

        self.app = app
        self.setWindowIcon(QIcon(const.MAIN_ICON))
        self.setWindowTitle(const.MAIN_WINDOW_TITLE)

        view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, *const.AREA_SIZE))
        felt = QBrush(QPixmap(f'{const.BG_DIR}/default.bmp'))
        self.scene.setBackgroundBrush(felt)
        view.setScene(self.scene)
        self.init_menu_actions()

        sb_scales = (1, 2, 0)
        self.status_labels = []
        for i in range(3):
            self.status_labels.append(QLabel())
            self.statusBar().addWidget(self.status_labels[i], sb_scales[i])

        # view.setFocusPolicy(Qt.StrongFocus)
        self.setCentralWidget(view)
        self.setFixedSize(*const.WINDOW_SIZE)
        self.resize(*const.WINDOW_SIZE)
        self.center()
        self.show()

    def init_menu_actions(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Файл')
        # toolbar = self.addToolBar('Выход')
        start_actn = QAction(QIcon(const.MAIN_ICON), 'Играть', self)
        start_actn.setShortcut('F2')
        start_actn.setStatusTip('Начать новую игру')
        start_actn.triggered.connect(self.start_game)
        file_menu.addAction(start_actn)

        file_menu.addSeparator()
        exit_actn = QAction(QIcon(f'{const.RES_DIR}/exit.ico'), 'Выход', self)
        exit_actn.setShortcut('Esc')
        exit_actn.setStatusTip('Выход из игры')
        exit_actn.triggered.connect(self.close)
        file_menu.addAction(exit_actn)
        # toolbar.addAction(exit_actn)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, 10)  # (screen.height() - size.height()) / 3)

    def closeEvent(self, event):
        super(MainWnd, self).closeEvent(event)

    def set_status_messages(self, messages):
        """
        Записать сообщение в статусбар

        :param messages: list, tuple: массив сообщений. Сообщения распределяются по индексам:
            0 - в первую панель статусбара (слева - направо), 1 - во вторую и т.д.
            Длина списка сообщений не должна превышать кол-во панелей статусбара. Все, что больше, будет игнорироваться
        """

        for i in range(len(messages)):
            if i < len(self.status_labels):
                self.status_labels[i].setText(messages[i])

    def set_status_message(self, message, index=0):
        """
        Записать сообщение в статусбар

        :param message: str: Строка сообщения.
        :param index: int: Индекс панели статусбара, где надо вывести сообщение
        """

        if 0 < index < len(self.status_labels):
            self.status_labels[index].setText(message)

    def clear_status_messages(self):
        self.set_status_messages(('', '', ''))

    def add_label(self, size, position, font_size, font_weight, color=None, text=None, tooltip=None):
        """
        Добавляет на форму элемент QLabel

        :param tuple size: размеры элемента: (width, height)
        :param tuple position: расположение начала элемента (x, y)
        :param int font_size: размер шрифта
        :param int font_weight: жирность шрифта
        :param str color: цвет текста, в формате html (название цвета, строка с hex-представлением и т.д.)
        :param str text: начальный текст
        :param str tooltip: всплывающая подсказка
        :return: QLabel
        """

        lb = QLabel(text)
        f = lb.font()
        f.setWeight(font_weight)
        f.setPointSize(font_size)
        lb.setFont(f)
        if color:
            lb.setStyleSheet(''.join(('QLabel {color:', color, '}')))
        lb.setToolTip(tooltip)
        lb.resize(*size)
        lb.move(*position)
        self.layout().addWidget(lb)

        return lb

    def add_button(self, callback, label=None, size=None, position=None, font_size=None, font_weight=None,
                   bg_color=None, font_color=None):
        """
        Добавляет на форму элемент QPushButton

        :param callable callback: функция обработчик нажатия
        :param str label: Надпись на кнопке
        :param tuple size: Размер кнопки
        :param tuple position: Положение кнопки
        :param int font_size: Размер шрифта подписи
        :param int font_weight: Жирность шрифта подписи
        :param str bg_color: цвет фона, в формате html (название цвета, строка с hex-представлением и т.д.)
        :param str font_color: цвет подписи, в формате html (название цвета, строка с hex-представлением и т.д.)
        :return: QPushButton
        """

        btn = QPushButton(label)

        if font_size is not None or font_weight is not None:
            f = btn.font()
            if font_weight is not None:
                f.setWeight(65)
            if font_size is not None:
                f.setPointSize(16)
            btn.setFont(f)

        if bg_color or font_color:
            style = 'QPushButton {0}{1}{2}{3}'
            bg = f'background-color: {bg_color}; ' if bg_color else ''
            c = f'color: {font_color}' if font_color else ''
            btn.setStyleSheet(style.format('{', bg, c, '}'))

        if size:
            btn.resize(*size)

        if position:
            btn.move(*position)

        btn.clicked.connect(callback)
        self.layout().addWidget(btn)
        return btn

    def remove_widget(self, widget):
        if widget:
            self.layout().removeWidget(widget)
            widget.deleteLater()

    def started(self):
        return self.game and self.game.started()

    def set_default_options(self):
        self.options['game_sum_by_diff'] = True
        self.options['dark_allowed'] = False
        self.options['third_pass_limit'] = False
        self.options['fail_subtract_all'] = False
        self.options['no_joker'] = False
        self.options['joker_give_at_par'] = False
        self.options['joker_demand_peak'] = True
        self.options['pass_factor'] = 5
        self.options['gold_mizer_factor'] = 15
        self.options['dark_notrump_factor'] = 20
        self.options['brow_factor'] = 50
        self.options['dark_mult'] = 2
        self.options['gold_mizer_on_null'] = True
        self.options['on_all_order'] = True
        self.options['take_block_bonus'] = True

    def start_game(self):
        """ Старт игры - инициализация игры и показ игрового поля """

        self.stop_game()

        # Настройка договоренностей игры, игроков и т.п.
        # todo: Пока что накидываем все опции дефолтно, без возможности выбора. Потом сделаю форму
        robots = [r for r in const.ROBOTS]
        humans = [h for h in const.HUMANS]
        self.players = []
        self.bet = 10
        self.set_default_options()
        self.deck_type = random.choice(const.DECK_TYPE)
        self.back_type = random.randint(1, 9)
        self.order_dark = None

        for i in range(random.choice([3, 4])):
            if i == 0:
                self.players.append(helpers.Player())
                self.players[i].id = i
                self.players[i].is_robot = False
                self.players[i].name = f'{humans.pop(random.randrange(0, len(humans)))}'
            else:
                self.players.append(helpers.Player())
                self.players[i].id = i
                self.players[i].is_robot = True
                self.players[i].name = f'{robots.pop(random.randrange(0, len(robots)))}'
                self.players[i].risk_level = random.randint(0, 2)

        self.options['deal_types'] = [n for n in range(len(eng_const.DEAL_NAMES))]

        self.game = engine.Engine(self.players, self.bet, allow_no_human=False, **self.options)
        self.game.start()

        # И поехала игра
        if self.game.started():
            self.is_new_round = True
            self.init_game_table()
            self.next()

    def stop_game(self):
        """ Остановить игру, очистить игровое поле """

        if self.started():
            self.game.stop()

        self.players = []
        self.clear()

    def clear(self):
        """ Очистка всех компонентов формы по окончании игры """

        self.clear_buttons()
        self.clear_player_labels()
        self.clear_table()

        self.remove_widget(self.table_label)
        self.table_label = None

        self.remove_widget(self.next_button)
        self.next_button = None

        self.remove_widget(self.deal_label)
        self.deal_label = None

        self.remove_widget(self.first_move_label)
        self.first_move_label = None

        self.remove_widget(self.order_info_label)
        self.order_info_label = None

        self.scene.clear()

    def init_game_table(self):
        """ Показ игрового поля, отображение на нем игроков """
        if len(self.players) == 4:
            pos = (20, 45)
        else:
            pos = (round(const.WINDOW_SIZE[0] / 2) - round(const.INFO_AREA_SIZE[0] / 2) + 5, 45)

        fp = self._get_face_positions()
        ap = self._get_area_positions()
        lo = self._get_label_offsets()
        self.draw_table_area()

        self.deal_label = self.add_label((const.INFO_AREA_SIZE[0] - const.CARD_SIZE[0] - 20, 37),
                                         (pos[0] + 5, pos[1] + 5), 18, 65)

        self.first_move_label = self.add_label((const.INFO_AREA_SIZE[0] - const.CARD_SIZE[0] - 20, 32),
                                               (pos[0] + 5, pos[1] + 50), 16, 65, color='Aqua')

        self.order_info_label = self.add_label((const.INFO_AREA_SIZE[0] - const.CARD_SIZE[0] - 20, 32),
                                               (pos[0] + 5, pos[1] + 100), 16, 65)

        for i, p in enumerate(self.players):
            if i == 0:
                sz = const.WINDOW_SIZE[0] - 30, const.PLAYER_AREA_SIZE[1] - 10
            else:
                sz = const.PLAYER_AREA_SIZE

            area = Area(self, sz)
            area.setPos(*ap[i])
            self.scene.addItem(area)

            player = Face(p)
            player.setPos(*fp[i])
            self.scene.addItem(player)

            if p.is_robot:
                self.set_text(p.name, (ap[i][0] + 3, fp[i][1] + const.FACE_SIZE[1]), Qt.cyan, 18, 65)
                self.set_text(eng_const.RISK_LVL_NAMES[p.risk_level], (ap[i][0] + 3, fp[i][1] + const.FACE_SIZE[1] + 30),
                              Qt.gray, 13, 65)
                self.add_player_label(i, 'order', '', (ap[i][0] + const.FACE_SIZE[0] + lo[i][0], ap[i][1] + lo[i][1]),
                                      'Aqua', 16, 70)
                self.add_player_label(i, 'take', '', (ap[i][0] + const.FACE_SIZE[0] + lo[i][0], ap[i][1] + lo[i][1] + 35),
                                      'Aqua', 16, 70)
            else:
                self.set_text(p.name, (ap[i][0] + 200, fp[i][1] + const.FACE_SIZE[1] + 15), Qt.cyan, 18, 65)
                self.add_player_label(i, 'order', '', (ap[i][0] + lo[i][0], ap[i][1] + lo[i][1]), 'Aqua', 16, 70)
                self.add_player_label(i, 'take', '', (ap[i][0] + lo[i][0], ap[i][1] + lo[i][1] + 35), 'Aqua', 16, 70)

    def set_text(self, text, position, color, size, weight):
        """
        Отрисовка текста на поле

        :param str text: текст, который будет написан
        :param list or tuple position: расположение начала текста (x, y)
        :param color: цвет текста, константа Qt.const или экземпляр Qt.Color
        :param int size: размер шрифта
        :param int weight: жирность шрифта
        """

        f = self.scene.font()
        f.setWeight(weight)
        f.setPointSize(size)
        t = self.scene.addText(text, f)
        t.setPos(*position)
        t.setDefaultTextColor(color)

    def add_player_label(self, player, type_, text, position, color, font_size, font_weight):
        """
        Добавляет на форму элемент QLabel, отражающий сведения о заказе или взятке, связанный с определенным игроком

        :param int player: индекс игрока, чьи сведения будем отображать
        :param str type_: тип метки - что будет показано - заказ ('order') или взятки ('take')
        :param str text: начальный текст
        :param list or tuple position: расположение начала элемента (x, y)
        :param str color: цвет текста, в формате html (название цвета, строка с hex-представлением и т.д.)
        :param int font_size: размер шрифта
        :param int font_weight: жирность шрифта
        """

        lb = self.add_label((90, 24), position, font_size, font_weight, color=color, text=text,
                            tooltip='Заказ' if type_ == 'order' else 'Взял')

        if player < len(self.labels):
            self.labels[player][type_] = lb
        else:
            self.labels.append({type_: lb})

    def clear_player_labels(self):
        """ Удаляет все элементы label, связанные с игроками, с формы """

        for o in self.labels:
            for k in o:
                self.remove_widget(o[k])

        self.labels = []

    def next(self):
        """ Обработка игрового цикла """

        if not self.started():
            self.stop_game()
            return

        if self.is_new_round:
            self.is_new_round = False
            self.clear_cards(True)
            self.draw_info_area()

        if self.game.status() == eng_const.EXT_STATE_WALKS:
            d = self.game.current_deal()
            self.draw_order()

            if self.game.is_bet():
                if self.game.dark_allowed and d.type_ not in (eng_const.DEAL_DARK, eng_const.DEAL_BROW) and self.order_dark is None:
                    self.show_dark_buttons()
                else:
                    self.draw_cards(self.order_dark or d.type_ == eng_const.DEAL_DARK, d.type_ != eng_const.DEAL_BROW)
                    self.show_order_buttons()
            else:
                self.draw_cards()
                self.draw_take()
                self.draw_table()
        elif self.game.status() == eng_const.EXT_STATE_LAP_PAUSE:
            self.draw_table(True)
            self.draw_cards()
            self.draw_take()

    def clear_cards(self, total=False):
        """
        Очистка всех карт с игрового стола

        :param total: Удалить вобще все карты, что возможно или только карты, помеченные как удаляемые (карты на уках игроков)
        """

        for w in self.scene.items():
            if isinstance(w, QCard) and (w.removable or total):
                self.scene.removeItem(w)

    def draw_cards(self, h_back_up=False, r_back_up=True):
        """
        Отрисовка карт на руках у игроков

        :param h_back_up: отобразить карты человека рубашкой вверх или вниз
        :param r_back_up: отобразить карты компьютерных игроков рубашкой вверх или вниз
        """

        ap = self._get_area_positions()
        self.clear_cards()

        for i, p in enumerate(self.players):
            if not p.is_robot:
                start_x = const.PLAYER_AREA_SIZE[0]
                for n, card in enumerate(p.cards):
                    qc = QCard(self, card, p, self.deck_type, f'back{self.back_type}')
                    if h_back_up:
                        qc.turn_back_up()
                    else:
                        qc.turn_face_up()
                    qc.setPos(start_x + (const.CARD_SIZE[0] + 5) * n, ap[i][1] + 5)
                    self.scene.addItem(qc)
            else:
                if i == len(self.players) - 1:
                    start_x = ap[i][0] + 5
                else:
                    start_x = ap[i][0] + const.FACE_SIZE[0] + 98 - len(p.cards) * const.CARD_OFFSET[0]

                for n, card in enumerate(p.cards):
                    qc = QCard(self, card, p, self.deck_type, f'back{self.back_type}')
                    qc.setZValue(const.CARD_BASE_Z_VALUE + n)
                    if r_back_up:
                        qc.turn_back_up()
                    else:
                        qc.turn_face_up()
                    qc.setPos(start_x + const.CARD_OFFSET[0] * n, ap[i][1] + 5 + const.CARD_OFFSET[1] * n)
                    self.scene.addItem(qc)

    def draw_info_area(self):
        """ Отрисовка информации о раздаче в начале раунда (тип раздачи, козырь, чей первый ход) """

        if len(self.players) == 4:
            pos = (-35, 10)
        else:
            pos = (round(const.AREA_SIZE[0] / 2) - round(const.INFO_AREA_SIZE[0] / 2), 10)

        area = Area(self, const.INFO_AREA_SIZE)
        area.setPos(*pos)
        self.scene.addItem(area)

        d = self.game.current_deal()
        if d.type_ == eng_const.DEAL_NO_TRUMP:
            c = 'Lime'
        elif d.type_ == eng_const.DEAL_DARK:
            c = 'Gray'
        elif d.type_ == eng_const.DEAL_GOLD:
            c = 'Yellow'
        elif d.type_ == eng_const.DEAL_MIZER:
            c = 'OrangeRed'
        elif d.type_ == eng_const.DEAL_BROW:
            c = 'Fuchsia'
        else:
            c = 'Honeydew'

        if d.type_ < 3:
            text = 'Кон по {0} карт{1}'.format(d.cards, 'е' if d.cards == 1 else '')
        else:
            text = eng_const.DEAL_NAMES[d.type_]
        self.deal_label.setStyleSheet('QLabel {color: %s}' % c)
        self.deal_label.setText(text)

        tl, tc = self.game.trump()
        if tc:
            if tc.joker:
                hint = 'нет'
            else:
                clr = 'red' if tc.lear > 1 else 'navy'
                hint = f'<span style="color:{clr}">{eng_const.LEAR_SYMBOLS[tc.lear]}</span>'

            qc = QCard(self, tc, None, self.deck_type, f'back{self.back_type}', removable=False,
                       tooltip=f'Козырь: {hint}', replace_tooltip=True)
            qc.turn_face_up()
            qc.setPos(pos[0] + const.INFO_AREA_SIZE[0] - const.CARD_SIZE[0] - 5, pos[1] + 5)
            self.scene.addItem(qc)
        else:
            f = Lear(tl)
            f.setPos(pos[0] + const.INFO_AREA_SIZE[0] - 25, pos[1] + 5)
            self.scene.addItem(f)

        self.first_move_label.setText(f'Первый ход: {self.game.players[d.player].name}')

    def draw_table_area(self):
        """ Отрисовка области расположения карт, которыми ходили """

        pos = (round(const.AREA_SIZE[0] / 2) - round(const.TABLE_AREA_SIZE[0] / 2),
               round(const.AREA_SIZE[1] / 2) - round(const.TABLE_AREA_SIZE[1] / 2))

        area = Area(self, const.TABLE_AREA_SIZE)
        area.setPos(*pos)
        self.scene.addItem(area)

        self.table_label = self.add_label((const.TABLE_AREA_SIZE[0] - 20, 24), (pos[0] + 60, pos[1] + 35), 13, 65,
                                          color='Yellow')
        self.table_label.setAlignment(Qt.AlignHCenter)

        self.next_button = self.add_button(self.next_button_click, 'Далее', (150, 50), (pos[0] + 230, pos[1] + 70),
                                           16, 65, 'DarkGreen', 'Lime')
        self.next_button.hide()

    def draw_table(self, overall=False):
        """ Отрисовка игрового поля """

        pos = (round(const.AREA_SIZE[0] / 2) - 40, round(const.AREA_SIZE[1] / 2) - 10)
        ofs = self._get_table_offsets()

        for pi, ti in self.game.table().items():
            if pi not in self.table:
                qc = QCard(self, ti.card, self.players[pi], self.deck_type, f'back{self.back_type}', removable=False,
                           tooltip=f'{self.players[pi].name}:')
                qc.turn_face_up()
                qc.setPos(pos[0] + ofs[pi][0], pos[1] + ofs[pi][1])
                self.table[pi] = qc
                self.scene.addItem(qc)

                if ti.is_joker():
                    self.table_label.setText(f'{self.players[pi].name}: Джокер: {self._get_joker_info(ti.card)}')

                if ti.order == 0:
                    qc.set_color_shadow()

        if overall:
            i, p = self.game.take_player()
            self.table_label.setText(f'Взял: {p.name}')
            self.next_button.show()

    def clear_table(self):
        """ Очистка всех элементов с игрового стола """

        if self.table_label:
            self.table_label.setText('')

        if self.next_button:
            self.next_button.hide()

        for k in self.table:
            if isinstance(self.table[k], QCard):
                self.scene.removeItem(self.table[k])

        self.table = {}

    def draw_order(self):
        """ Отрисовка заказа игроков """

        show = True
        n = 0

        for i, p in enumerate(self.players):
            if p.order > -1:
                self.labels[i]['order'].setText('{0}{1}'.format(p.order, '*' if p.order_is_dark else ''))
                n += p.order
            else:
                show = False

        if show:
            diff = n - self.game.current_deal().cards
            self.order_info_label.setStyleSheet('QLabel {color: %s}' % '{0}'.format('Lime' if diff < 0 else 'OrangeRed'))
            self.order_info_label.setText('{0} {1}'.format('Перебор ' if diff < 0 else 'Недобор', abs(diff)))

    def draw_take(self):
        """ Отрисовка взяток игроков """

        for i, p in enumerate(self.players):
            self.labels[i]['take'].setText(f'{p.take}')

            if p.order > p.take:
                self.labels[i]['take'].setStyleSheet('QLabel {color: OrangeRed}')
            elif p.order < p.take:
                self.labels[i]['take'].setStyleSheet('QLabel {color: Fuchsia}')
            else:
                self.labels[i]['take'].setStyleSheet('QLabel {color: Lime}')

    def show_dark_buttons(self):
        """ Показ кнопок выбора как заказывать - в темную или в светлую """

        self.table_label.setText('Твой заказ')

        btnd = self.add_button(lambda: self.dark_btn_click(True), 'В темную', (150, 50),
                               (round(const.AREA_SIZE[0] / 2) - 150 / 2 - 40, round(const.AREA_SIZE[1] / 2)),
                               16, 65, 'DarkRed', 'DarkOrange')
        self.buttons.append(btnd)

        btnl = self.add_button(lambda: self.dark_btn_click(False), 'В светлую', (150, 50),
                               (round(const.AREA_SIZE[0] / 2) + 150 / 2 + 5, round(const.AREA_SIZE[1] / 2)),
                               16, 65, 'DarkGreen', 'Lime')
        self.buttons.append(btnl)

    def show_order_buttons(self):
        """ Показ кнопок заказа """

        self.table_label.setText('Твой заказ')

        cols = round(36 / self.game.party_size() / 2) + 1
        coef = min(self.game.current_deal().cards + 1, cols)
        x = round(const.AREA_SIZE[0] / 2) - round((55 * coef) / 2)

        for i in range(self.game.current_deal().cards + 1):
            x = x + 55 * i
            if i <= cols:
                y = round(const.AREA_SIZE[1] / 2)
            else:
                y = round(const.AREA_SIZE[1] / 2) + 60

            btn = self.add_button(lambda state, z=i: self.order_btn_click(z), f'{i}', (50, 50), (x, y),
                                   16, 65, 'DarkGreen', 'Lime')
            self.buttons.append(btn)

    def clear_buttons(self):
        """ Убирает все кнопки с игрового стола """

        for btn in self.buttons:
            self.remove_widget(btn)

        self.buttons = []

        if self.table_label:
            self.table_label.setText('')

    def dark_btn_click(self, is_dark):
        """
        Обработка нажатия кнопок выбора типа заказа: в темную или в светлую

        :param bool is_dark: флаг в темную или нет
        """

        self.order_dark = is_dark
        self.clear_buttons()
        self.next()

    def order_btn_click(self, order):
        """
        Обработка нажатия кнопок заказа

        :param int order: сделанный заказ
        """

        try:
            self.game.make_order(order, self.order_dark or False)
            self.game.give_walk()
            self.game.next()
        except helpers.GameException as e:
            QMessageBox.warning(self, 'Заказ', f'{e}', QMessageBox.Ok)

        self.clear_buttons()
        self.next()

    def card_click(self, card):
        """
        Обработка нажатия на карты

        :param QCard card: карта, на которую нажали
        """

        c = card.card
        p = card.player

        if self.started() and p and not p.is_robot and self.game.status() == eng_const.EXT_STATE_WALKS and not self.game.is_bet():
            try:
                if c.joker:
                    # todo: сделать показ контролов выбора действий джокером
                    pass
                else:
                    self.game.do_walk(p.cards.index(c))
                    self.game.give_walk()
                    self.game.next()
            except helpers.GameException as e:
                QMessageBox.warning(self, 'Ход', f'{e}', QMessageBox.Ok)

            self.next()

    def next_button_click(self):
        if self.started():
            self.game.next()
            self.next()

    def _get_face_positions(self):
        """ Позиции для отрисовки аватарок игроков """

        if len(self.players) == 4:
            return (
                (-30, const.AREA_SIZE[1] - const.FACE_SIZE[1] - 68),  # позиция человека, низ центр
                (-30, round(const.AREA_SIZE[1] / 2) - const.FACE_SIZE[1] + 5),  # лево центр
                (round(const.AREA_SIZE[0] / 2) - const.FACE_SIZE[0] + 5, 15),  # верх центр
                (const.AREA_SIZE[0] - const.FACE_SIZE[0] + 30, round(const.AREA_SIZE[1] / 2) - const.FACE_SIZE[1] + 5)  # право центр
            )
        else:
            return (
                (-30, const.AREA_SIZE[1] - const.FACE_SIZE[1] - 68),  # позиция человека, низ центр
                (-30, 15),  # левый верхний угол
                (const.AREA_SIZE[0] - const.FACE_SIZE[0] + 30, 15)  # правый верхний угол
            )

    def _get_area_positions(self):
        """ Позиции расположения областей игроков """

        if len(self.players) == 4:
            return (
                (-35, const.AREA_SIZE[1] - const.PLAYER_AREA_SIZE[1]),  # позиция человека, низ центр
                (-35, round(const.AREA_SIZE[1] / 2) - const.FACE_SIZE[1]),  # лево центр
                (round(const.AREA_SIZE[0] / 2) - const.FACE_SIZE[0], 10),  # верх центр
                (const.AREA_SIZE[0] - const.PLAYER_AREA_SIZE[0] + 35, round(const.AREA_SIZE[1] / 2) - const.FACE_SIZE[1])  # право центр
            )
        else:
            return (
                (-35, const.AREA_SIZE[1] - const.PLAYER_AREA_SIZE[1]),  # позиция человека, низ центр
                (-35, 10),  # левый верхний угол
                (const.AREA_SIZE[0] - const.PLAYER_AREA_SIZE[0] + 35, 10)  # правый верхний угол
            )

    def _get_label_offsets(self):
        """ Координаты смещения положения лабелов с информацией игроков """

        if len(self.players) == 4:
            return (
                (250, 40),  # позиция человека, низ центр
                (65, 40),  # лево центр
                (65, 40),  # верх центр
                (45, 40)  # право центр
            )
        else:
            return (
                (250, 40),  # позиция человека, низ центр
                (65, 40),  # левый верхний угол
                (45, 40)  # правый верхний угол
            )

    def _get_table_offsets(self):
        """ Координаты смещения положения карт в области ходов """

        if len(self.players) == 4:
            return (
                (0, const.CARD_SIZE[1] + 10),  # позиция человека, низ центр
                (-const.CARD_SIZE[0] - 10, 0),  # лево центр
                (0, -const.CARD_SIZE[1] - 10),  # верх центр
                (const.CARD_SIZE[0] + 10, 0)  # право центр
            )
        else:
            return (
                (0, const.CARD_SIZE[1] + 10),  # позиция человека, низ центр
                (-const.CARD_SIZE[0] - 10, -const.CARD_SIZE[1] - 10),  # левый верхний угол
                (const.CARD_SIZE[0] + 10, -const.CARD_SIZE[1] - 10)  # правый верхний угол
            )

    def _get_joker_info(self, card):
        if card.joker:
            if card.joker_action == eng_const.JOKER_TAKE:
                s, l = 'Самая крупная', eng_const.LEAR_SYMBOLS[card.joker_lear]
            elif card.joker_action == eng_const.JOKER_TAKE_BY_MAX:
                s, l = 'Забираю по старшей', eng_const.LEAR_SYMBOLS[card.joker_lear]
            elif card.joker_action == eng_const.JOKER_GIVE:
                s, l = 'Скидываю как ', eng_const.LEAR_SYMBOLS[card.joker_lear] if not self.game.joker_give_at_par else f'{card}'
            else:
                s, l = None, None

            return '{0} {1}'.format(s, l)
        else:
            return ''
