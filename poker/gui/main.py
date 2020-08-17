import os
import random

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import utils, const
from game import engine, helpers, const as eng_const


class QCard(QGraphicsPixmapItem):

    def __init__(self, card: helpers.Card, deck, back, *args):
        super(QCard, self).__init__(*args)

        self.card = card
        self.deck = deck
        self.back = back
        self.side = const.CARD_SIDE_BACK

        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.face = QPixmap(f'{const.CARD_DECK_DIR}/{self.deck}/{self.card.value}{self.card.lear}.bmp')
        self.back = QPixmap(f'{const.CARD_BACK_DIR}/{self.back}.bmp')

    def turn_face_up(self):
        self.side = const.CARD_SIDE_FACE
        self.setPixmap(self.face)

    def turn_back_up(self):
        self.side = const.CARD_SIDE_BACK
        self.setPixmap(self.back)

    def mousePressEvent(self, e):
        # тут обрабатываем клик мышкой
        super(QCard, self).mousePressEvent(e)


class Face(QGraphicsPixmapItem):

    def __init__(self, player, *args):
        super(Face, self).__init__(*args)
        self.player = player
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
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

    def mousePressEvent(self, e):
        # по клику мышкой возможно что-то будет - показ подробной инфы про игрока например
        super(Face, self).mousePressEvent(e)


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


class MainWnd(QMainWindow):

    def __init__(self, app):
        super().__init__()

        self.options = {}
        self.players = []
        self.bet = None
        self.game = None

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
        # self.setFixedSize(*const.WINDOW_SIZE)
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

    def show_help(self):
        QMessageBox.information(self.parent(), 'Подсказка',
                                '\n'.join(('Клавиши управления игрой\n',) + const.HELP_KEYS), QMessageBox.Ok)

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

        self.options['deal_types'] = [n for n in range(len(eng_const.DEAL_NAMES) - 1)]

        self.game = engine.Engine(self.players, self.bet, allow_no_human=False, **self.options)
        self.game.start()

        # И поехала игра
        if self.game.started():
            self.init_game_table()

    def stop_game(self):
        """ Остановить игру, очистить игровое поле """

        if self.game:
            self.game.stop()
        self.players = []
        self.scene.clear()

    def init_game_table(self):
        """ Показ игрового поля, отображение на нем игроков """

        fp = self._get_face_positions()
        ap = self._get_area_positions()

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
                self.set_text(p.name, (ap[i][0] + 3, fp[i][1] + const.FACE_SIZE[1]), Qt.black, 18, 65)
                self.set_text(eng_const.RISK_LVL_NAMES[p.risk_level], (ap[i][0] + 3, fp[i][1] + const.FACE_SIZE[1] + 30),
                              Qt.cyan, 13, 65)
            else:
                self.set_text(p.name, (ap[i][0] + 5, fp[i][1] + const.FACE_SIZE[1] + 15), Qt.black, 18, 65)

    def set_text(self, text, position, color, size, weight):
        f = self.scene.font()
        f.setWeight(weight)
        f.setPointSize(size)
        t = self.scene.addText(text, f)
        t.setPos(*position)
        t.setDefaultTextColor(color)

    def _get_face_positions(self):
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
