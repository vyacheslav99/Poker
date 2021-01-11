import os
import random
import pickle
import json

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from modules.core import engine, helpers, const as core_const
from modules.params import Params, Options, Profiles
from gui import const, utils
from gui.graphics import QCard, Face, Lear, Area
from gui.game_table import GameTableDialog
from gui.service_info import ServiceInfoDialog
from gui.players_dlg import PlayersDialog
from gui.agreements_dlg import AgreementsDialog
from gui.settings_dlg import SettingsDialog
from gui.profiles_dlg import ProfilesDialog


class MainWnd(QMainWindow):

    def __init__(self, app, *args):
        super().__init__()

        self.app = app
        self.__dev_mode = '--dev_mode' in args
        self.params = Params(filename=const.PARAMS_FILE if os.path.exists(const.PARAMS_FILE) else None)
        self.profiles = Profiles(filename=const.PROFILES_FILE if os.path.exists(const.PROFILES_FILE) else None)
        self.options = Options()
        self.curr_profile = None

        self._started = False
        self.players = []
        self.table = {}
        self.game = None
        self.is_new_round = False
        self.is_new_lap = False
        self.order_dark = None
        self.joker_walk_card = None
        self.can_show_results = False

        self.buttons = []
        self.labels = []
        self.table_label = None
        self.next_button = None
        self.deal_label = None
        self.first_move_label = None
        self.order_info_label = None
        self.ja_take_btn = None
        self.ja_take_by_btn = None
        self.ja_give_btn = None
        self.grid_stat_button = None
        self.game_table = None
        self.ja_lear_buttons = []
        self.round_result_labels = []
        self.service_wnd = None
        self.sb_label = None

        self.start_actn = None
        self.throw_actn = None
        self.svc_actn = None

        self.init_profile()
        self.setWindowIcon(QIcon(const.MAIN_ICON))
        self.setWindowTitle(const.MAIN_WINDOW_TITLE)

        view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, *const.AREA_SIZE))
        felt = QBrush(QPixmap(f'{const.BG_DIR}/default.bmp'))
        self.scene.setBackgroundBrush(felt)
        view.setScene(self.scene)
        self.init_menu_actions()

        # view.setFocusPolicy(Qt.StrongFocus)
        self.setCentralWidget(view)
        self.setFixedSize(*const.WINDOW_SIZE)
        self.resize(*const.WINDOW_SIZE)
        self.center()
        self.show()

    def init_menu_actions(self):
        menubar = self.menuBar()

        # Меню Файл
        menu = menubar.addMenu('Файл')
        # toolbar = self.addToolBar('Выход')
        self.start_actn = QAction(QIcon(const.MAIN_ICON), 'Начать', self)
        self.start_actn.setShortcut('F2')
        self.start_actn.triggered.connect(self.on_start_action)
        menu.addAction(self.start_actn)

        self.throw_actn = QAction('Бросить партию', self)
        self.throw_actn.setStatusTip('Отказаться от текущей партии')
        self.throw_actn.triggered.connect(self.on_throw_action)
        menu.addAction(self.throw_actn)

        if self.__dev_mode:
            self.svc_actn = QAction(QIcon(f'{const.RES_DIR}/svc.ico'), 'Служебная информация', self)
            self.svc_actn.setShortcut('F9')
            self.svc_actn.setStatusTip('Показать окно со служебной информацией')
            self.svc_actn.triggered.connect(self.show_service_window)
            menu.addAction(self.svc_actn)

        menu.addSeparator()
        actn = QAction(QIcon(f'{const.RES_DIR}/exit.ico'), 'Выход', self)
        actn.setShortcut('Esc')
        actn.setStatusTip('Выход из игры')
        actn.triggered.connect(self.close)
        menu.addAction(actn)

        # Меню Настройка
        menu = menubar.addMenu('Настройка')
        actn = QAction(QIcon(f'{const.RES_DIR}/settings.ico'), 'Настройки', self)
        actn.setShortcut('F10')
        actn.triggered.connect(self.show_settings)
        menu.addAction(actn)

        actn = QAction(QIcon(f'{const.RES_DIR}/list.png'), 'Договоренности', self)
        actn.setShortcut('F5')
        actn.triggered.connect(self.show_agreements)
        menu.addAction(actn)

        actn = QAction(QIcon(f'{const.RES_DIR}/player.ico'), 'Профили', self)
        actn.setShortcut('F6')
        actn.triggered.connect(self.show_profiles)
        menu.addAction(actn)

        actn = QAction('Статистика', self)
        actn.setShortcut('F8')
        actn.triggered.connect(self.show_statistic)
        menu.addAction(actn)

        self.refresh_menu_actions()
        # toolbar.addAction(exit_actn)

    def refresh_menu_actions(self):
        """ Акуализация состояния игрового меню """

        if self.started():
            self.start_actn.setText('Отложить партию')
            self.start_actn.setStatusTip('Отложить партию.\nВы сможете продолжить ее позднее')
            self.throw_actn.setEnabled(True)
            if self.svc_actn:
                self.svc_actn.setEnabled(True)
        else:
            if self.save_exists()[0]:
                self.start_actn.setText('Продолжить партию')
                self.start_actn.setStatusTip('Вернуться к отложенной партии')
            else:
                self.start_actn.setText('Новая партия')
                self.start_actn.setStatusTip('Начать новую партию')
            self.throw_actn.setEnabled(False)
            if self.svc_actn:
                self.svc_actn.setEnabled(False)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, 10)  # (screen.height() - size.height()) / 3)

    def closeEvent(self, event):
        self.save_params()
        super(MainWnd, self).closeEvent(event)

    def show_service_window(self):
        if self.__dev_mode and self.started():
            if not self.service_wnd:
                self.service_wnd = ServiceInfoDialog(self)

            self.service_wnd.players = self.players
            self.service_wnd.show()

    def show_settings(self):
        prv_user = self.params.user
        dlg = SettingsDialog(self, self.params.as_dict(), self.profiles)

        try:
            result = dlg.exec()

            if result == 0:
                return

            self.params.from_dict(dlg.get_params())

            if self.params.user != prv_user:
                self.set_profile(self.params.user)

            self.save_params()
        finally:
            dlg.destroy()

    def show_agreements(self):
        dlg = AgreementsDialog(self, self.game.options_as_dict() if self.started() else self.options.as_dict())
        try:
            if self.started():
                dlg.deactivate()
            result = dlg.exec()

            if result == 0 or self.started():
                return

            self.options.from_dict(dlg.get_agreements())
            self.save_params()
        finally:
            dlg.destroy()

    def show_profiles(self):
        dlg = ProfilesDialog(self, self.profiles, self.params.user)
        try:
            # в форму передаем сам объект Profiles, сохраняем (или отменяем) изменения в каждом профиле прям там,
            # так что после закрытия диалога в профилях уже все изменения есть, остается только сохранить в файл
            dlg.exec()
            self.save_params()
        finally:
            dlg.destroy()

    def show_statistic(self):
        print('Statistic action')

    def set_status_message(self, message):
        """
        Записать сообщение в статусбар

        :param message: str: Строка сообщения.
        """

        if self.sb_label:
            self.statusBar().removeWidget(self.sb_label)

        self.sb_label = QLabel(message)
        self.statusBar().addPermanentWidget(self.sb_label, 1)

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
                f.setWeight(font_weight)
            if font_size is not None:
                f.setPointSize(font_size)
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
        return self._started

    def init_profile(self):
        """ Инициализация текущего профиля """

        if self.profiles.count() == 0:
            self.profiles.create()

        if not self.params.user or not self.profiles.get(self.params.user):
            self.params.user = self.profiles.profiles[0].uid

        self.set_profile(self.params.user)

    def set_profile(self, uid):
        """ Смена текущего профиля """

        self.params.user = uid
        self.curr_profile = self.profiles.get(uid)
        self.set_status_message(self.curr_profile.name)

        if os.path.exists(f'{self.get_profile_dir()}/options.json'):
            self.options = Options(filename=f'{self.get_profile_dir()}/options.json')
        else:
            self.options = Options()

    def on_start_action(self):
        """ Обработчик меню начала игры """

        if self.started():
            self.stop_game()
        else:
            self.start_game()

        self.refresh_menu_actions()

    def on_throw_action(self):
        """ Обработчик меню Бросить партию """

        res = QMessageBox.question(self, 'Подтверждение',
                                   'Хотите бросить партию? Продолжить ее уже будет невозможно.\n',
                                   QMessageBox.Yes | QMessageBox.No)

        if res == QMessageBox.No:
            return

        if self.started():
            self.stop_game()
            self.clear_save()

        self.refresh_menu_actions()

    def start_game(self):
        """ Старт игры - инициализация игры и показ игрового поля """

        if self.save_exists()[0]:
            return self.load_game()

        self.stop_game()

        # Настройка договоренностей игры, игроков и т.п.
        self.players = []
        self.order_dark = None
        self.joker_walk_card = None
        self.can_show_results = False

        # диалог настройки договоренностей
        if self.params.start_type in (const.GAME_START_TYPE_AGREEMENTS, const.GAME_START_TYPE_ALL):
            agreements_dlg = AgreementsDialog(self, self.options.as_dict())
            result = agreements_dlg.exec()
            if result == 0:
                return

            self.options.from_dict(agreements_dlg.get_agreements())
            agreements_dlg.destroy()

        # диалог настройки игроков (создаем всегда, но показываем только если включена опция)
        players_dlg = PlayersDialog(self, players_cnt=self.options.players_cnt - 1)
        if self.params.start_type in (const.GAME_START_TYPE_PLAYERS, const.GAME_START_TYPE_ALL):
            result = players_dlg.exec()
            if result == 0:
                players_dlg.destroy()
                return

        # Накидываем игроков
        players = players_dlg.get_players()
        players_dlg.destroy()
        self.players.append(self.curr_profile)
        for p in players:
            self.players.append(p)

        self.options.players_cnt = len(self.players)
        self.game = engine.Engine(self.players, allow_no_human=False, **self.options.as_dict())
        self.game.start()

        # И поехала игра
        self._started = True
        self.is_new_round = True
        self.init_game_table()
        self.next()

    def load_game(self):
        """ Загрузка сохраненной игры """

        self.stop_game()
        self.can_show_results = False
        b, fn = self.save_exists()

        if not b:
            return

        mt, eng = self.load_save_file(fn)

        # устанавливаем игровые переменные модуля
        self.order_dark = mt['order_dark']
        self.joker_walk_card = mt['joker_walk_card']
        self.is_new_lap = mt['is_new_lap']
        self.is_new_round = mt['is_new_round']

        # игровой движок
        self.game = eng
        self.players = self.game.players
        self._started = True

        # if self.game.started():
        # отрисуем игровой стол
        self.init_game_table()
        self.draw_info_area()
        # заполняем таблицу игры
        self.fill_game_table()
        # продолжаем игру
        self.next()

    def save_game(self):
        """ Сохранение игры """

        if not self.started():
            return

        o = {
            'order_dark': self.order_dark,
            'joker_walk_card': self.joker_walk_card,
            'is_new_lap': self.is_new_lap,
            'is_new_round': self.is_new_round
        }

        fn = f'{self.get_profile_dir()}/save/auto.psg'
        self.write_save_file(fn, o)

    def stop_game(self):
        """ Остановить игру, очистить игровое поле """

        if self.service_wnd:
            self.service_wnd.hide()

        if self.game and self.game.started():
            self.game.stop()

        self._started = False
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

        self.remove_widget(self.ja_give_btn)
        self.ja_give_btn = None

        self.remove_widget(self.ja_take_btn)
        self.ja_take_btn = None

        self.remove_widget(self.ja_take_by_btn)
        self.ja_take_by_btn = None

        self.remove_widget(self.grid_stat_button)
        self.grid_stat_button = None

        for btn in self.ja_lear_buttons:
            self.remove_widget(btn)
        self.ja_lear_buttons = []

        for lb in self.round_result_labels:
            self.remove_widget(lb)
        self.round_result_labels = []

        self.scene.clear()
        self.refresh_menu_actions()

    def clear_save(self):
        """ Удаляет ненужный файл автосохранения """

        b, fn = self.save_exists()

        if b:
            os.unlink(fn)

    def init_game_table(self):
        """ Отрисовка основных эл-тов игрового поля в начале игры """

        if self.game_table:
            self.game_table.destroy()
            self.game_table = None

        self.game_table = GameTableDialog(self.players, self)

        if len(self.players) == 4:
            pos = (20, 45)
            ipos = (-35, 10)
        else:
            pos = (round(const.WINDOW_SIZE[0] / 2) - round(const.INFO_AREA_SIZE[0] / 2) + 5, 45)
            ipos = (round(const.AREA_SIZE[0] / 2) - round(const.INFO_AREA_SIZE[0] / 2), 10)

        info_area = Area(self, const.INFO_AREA_SIZE)
        info_area.setPos(*ipos)
        self.scene.addItem(info_area)

        fp = self.get_face_positions()
        ap = self.get_area_positions()
        lo = self.get_label_offsets()
        self.draw_table_area()

        self.deal_label = self.add_label((const.INFO_AREA_SIZE[0] - const.CARD_SIZE[0] - 20, 37),
                                         (pos[0] + 5, pos[1] + 5), 18, 65)

        self.first_move_label = self.add_label((const.INFO_AREA_SIZE[0] - const.CARD_SIZE[0] - 20, 32),
                                               (pos[0] + 5, pos[1] + 50), 16, 65, color='Aqua')

        self.order_info_label = self.add_label((const.INFO_AREA_SIZE[0] - const.CARD_SIZE[0] - 20, 32),
                                               (pos[0] + 5, pos[1] + 100), 16, 65)

        self.grid_stat_button = self.add_button(self.show_statistics_grid, 'Запись игры', (160, 50),
                                                (pos[0] + const.INFO_AREA_SIZE[0] - 170, pos[1] + const.INFO_AREA_SIZE[1] - 60),
                                                12, 65, 'YellowGreen', 'Purple')

        for i, p in enumerate(self.players):
            if i == 0:
                sz = const.WINDOW_SIZE[0] - 30, const.PLAYER_AREA_SIZE[1] - 10
            else:
                sz = const.PLAYER_AREA_SIZE

            player_area = Area(self, sz)
            player_area.setPos(*ap[i])
            self.scene.addItem(player_area)

            player = Face(p)
            player.setPos(*fp[i])
            self.scene.addItem(player)

            if p.is_robot:
                self.set_text(p.name, (ap[i][0] + 3, fp[i][1] + const.FACE_SIZE[1]), Qt.cyan, 18, 65)
                self.set_text(core_const.RISK_LVL_NAMES[p.risk_level], (ap[i][0] + 3, fp[i][1] + const.FACE_SIZE[1] + 30),
                              Qt.gray, 13, 65)
                self.add_player_label(i, 'order', '', (ap[i][0] + const.FACE_SIZE[0] + lo[i][0], ap[i][1] + lo[i][1]),
                                      'Aqua', 16, 70)
                self.add_player_label(i, 'take', '', (ap[i][0] + const.FACE_SIZE[0] + lo[i][0], ap[i][1] + lo[i][1] + 35),
                                      'Aqua', 16, 70)
            else:
                self.set_text(p.name, (ap[i][0] + 200, fp[i][1] + const.FACE_SIZE[1] + 12), Qt.cyan, 18, 65)
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
        :return: QGraphicsTextItem
        """

        f = self.scene.font()
        f.setWeight(weight)
        f.setPointSize(size)
        t = self.scene.addText(text, f)
        t.setPos(*position)
        t.setDefaultTextColor(color)
        return t

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

        if not self.game.started():
            if self.can_show_results:
                self.clear_save()
                self.stop_game()
                self.show_game_results()
                self.show_statistics_grid()
                return
            else:
                self.can_show_results = True

        if self.is_new_round:
            self.is_new_round = False
            self.order_dark = None
            self.hide_order_and_take()
            self.hide_round_results()
            self.clear_cards(True)
            self.draw_info_area()

        if self.game.status() == core_const.EXT_STATE_WALKS:
            d = self.game.current_deal()
            self.draw_order()

            if self.game.is_bet():
                if self.game.dark_allowed and d.type_ not in (core_const.DEAL_DARK, core_const.DEAL_BROW) and self.order_dark is None:
                    self.show_dark_buttons()
                else:
                    self.draw_cards(self.order_dark or d.type_ in (core_const.DEAL_DARK, core_const.DEAL_BROW),
                                    d.type_ != core_const.DEAL_BROW)
                    self.show_order_buttons()
            else:
                if self.is_new_lap:
                    self.is_new_lap = False
                    self.clear_table()
                self.table_label.setText('Твой ход')
                self.draw_cards()
                self.draw_take()
                self.draw_table()
        elif self.game.status() == core_const.EXT_STATE_LAP_PAUSE:
            self.is_new_lap = True
            self.draw_table(True)
            self.draw_cards()
            self.draw_take()
        elif self.game.status() == core_const.EXT_STATE_ROUND_PAUSE:
            self.is_new_round = True
            self.clear_table()
            self.show_round_results()

        if self.service_wnd and self.service_wnd.isVisible():
            self.service_wnd.refresh()

        self.save_game()

    def clear_cards(self, total=False):
        """
        Очистка всех карт с игрового стола + значков мастей при полной очистке

        :param total: Удалить вобще все карты и значки мастей, что возможно
            или только карты, помеченные как удаляемые (карты на уках игроков)
        """

        for w in self.scene.items():
            if (isinstance(w, QCard) and (w.removable or total)) or (total and isinstance(w, Lear)):
                self.scene.removeItem(w)

    def draw_cards(self, h_back_up=False, r_back_up=True):
        """
        Отрисовка карт на руках у игроков

        :param h_back_up: отобразить карты человека рубашкой вверх или вниз
        :param r_back_up: отобразить карты компьютерных игроков рубашкой вверх или вниз
        """

        ap = self.get_area_positions()
        self.clear_cards()

        for i, p in enumerate(self.players):
            if not p.is_robot:
                start_x = const.PLAYER_AREA_SIZE[0]
                cards = utils.sort_cards(p.cards, self.params.sort_order, self.params.lear_order)

                for n, card in enumerate(cards):
                    qc = QCard(self, card, p, self.params.deck_type, f'back{self.params.back_type}')
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
                    qc = QCard(self, card, p, self.params.deck_type, f'back{self.params.back_type}')
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

        d = self.game.current_deal()
        if d.type_ == core_const.DEAL_NO_TRUMP:
            c = 'Lime'
        elif d.type_ == core_const.DEAL_DARK:
            c = 'Black'
        elif d.type_ == core_const.DEAL_GOLD:
            c = 'Yellow'
        elif d.type_ == core_const.DEAL_MIZER:
            c = 'OrangeRed'
        elif d.type_ == core_const.DEAL_BROW:
            c = 'Fuchsia'
        else:
            c = 'LightCyan'

        if d.type_ < 3:
            if d.cards == 1:
                letter = 'е'
            elif d.cards < 5:
                letter = 'ы'
            else:
                letter = ''
            text = 'Кон по {0} карт{1}'.format(d.cards, letter)
        else:
            text = core_const.DEAL_NAMES[d.type_]
        self.deal_label.setStyleSheet('QLabel {color: %s}' % c)
        self.deal_label.setText(text)

        tl, tc = self.game.trump()
        if tc:
            if tc.joker:
                hint = 'нет (Бескозырка)'
            else:
                clr = 'red' if tc.lear > 1 else 'navy'
                hint = f'<span style="color:{clr}">{core_const.LEAR_SYMBOLS[tc.lear]}</span>'

            qc = QCard(self, tc, None, self.params.deck_type, f'back{self.params.back_type}', removable=False,
                       tooltip=f'Козырь: {hint}', replace_tooltip=True)
            qc.turn_face_up()
            qc.setPos(pos[0] + const.INFO_AREA_SIZE[0] - const.CARD_SIZE[0] - 5, pos[1] + 5)
            self.scene.addItem(qc)
        else:
            f = Lear(tl)
            f.setPos(pos[0] + const.INFO_AREA_SIZE[0] - 55, pos[1] + 5)
            self.scene.addItem(f)

        self.first_move_label.setText(f'Первый ход: {self.game.players[d.player].name}')

    def draw_table_area(self):
        """ Отрисовка области расположения карт, которыми ходили. Делаем один раз в начале игры """

        pos = (round(const.AREA_SIZE[0] / 2) - round(const.TABLE_AREA_SIZE[0] / 2),
               round(const.AREA_SIZE[1] / 2) - round(const.TABLE_AREA_SIZE[1] / 2))

        area = Area(self, const.TABLE_AREA_SIZE)
        area.setPos(*pos)
        self.scene.addItem(area)

        self.table_label = self.add_label((const.TABLE_AREA_SIZE[0] - 20, 34), (pos[0] + 60, pos[1] + 35), 13, 65,
                                          color='Yellow')
        self.table_label.setAlignment(Qt.AlignHCenter)

        self.next_button = self.add_button(self.next_button_click, 'Далее', (150, 50), (pos[0] + 230, pos[1] + 70),
                                           16, 65, 'DarkGreen', 'Lime')
        self.next_button.hide()

        jx = pos[0] + 65
        jy = pos[1] + const.TABLE_AREA_SIZE[1] - 45
        self.ja_take_btn = self.add_button(lambda: self.joker_action_btn_click(core_const.JOKER_TAKE), 'ЗАБРАТЬ',
                                           (150, 60), (jx, jy), 12, 65, 'Green', 'Yellow')
        self.ja_take_btn.hide()

        self.ja_take_by_btn = self.add_button(lambda: self.joker_action_btn_click(core_const.JOKER_TAKE_BY_MAX),
                                              'ПО СТАРШИМ', (150, 60), (jx + 160, jy), 12, 65, 'Green', 'Yellow')
        self.ja_take_by_btn.hide()

        self.ja_give_btn = self.add_button(lambda: self.joker_action_btn_click(core_const.JOKER_GIVE), 'СКИНУТЬ',
                                           (150, 60), (jx + 320, jy), 12, 65, 'Green', 'Yellow')
        self.ja_give_btn.hide()

        x = pos[0] + 130
        for i, lear in enumerate(const.LEARS):
            x = x + 60
            btn = self.add_button(lambda a, b=i: self.ja_select_lear_btn_click(b), size=(50, 50), position=(x, jy),
                                  bg_color='LightCyan')
            btn.setIcon(QIcon(f'{const.SUITS_DIR}/{lear}.png'))
            btn.setToolTip(core_const.LEAR_NAMES[i])
            btn.hide()
            self.ja_lear_buttons.append(btn)

        pos = self.get_round_info_positions()
        aligns = self.get_round_info_aligns()

        for i, p in enumerate(self.players):
            if i == 0:
                w = const.TABLE_AREA_SIZE[0] - 10
            else:
                w = round(const.TABLE_AREA_SIZE[0] / 2)

            lb = self.add_label((w, 150), (pos[i][0], pos[i][1]), 13, 65, color='aqua')
            lb.setAlignment(aligns[i])
            lb.setTextFormat(Qt.RichText)

            lb.hide()
            self.round_result_labels.append(lb)

    def draw_table(self, overall=False):
        """ Отрисовка игрового поля. Выполняем после каждого хода """

        pos = (round(const.AREA_SIZE[0] / 2) - 40, round(const.AREA_SIZE[1] / 2) - 10)
        ofs = self.get_table_offsets()

        for pi, ti in self.game.table().items():
            if pi not in self.table:
                qc = QCard(self, ti.card, self.players[pi], self.params.deck_type, f'back{self.params.back_type}',
                           removable=False, tooltip=f'{self.players[pi].name}:')
                qc.turn_face_up()
                qc.setPos(pos[0] + ofs[pi][0], pos[1] + ofs[pi][1])
                self.table[pi] = qc
                self.scene.addItem(qc)

                if ti.card.joker:
                    txt = f'Джокер: {self.get_joker_info(ti.card)}'
                    self.table_label.setText(f'{self.players[pi].name}: {txt}')
                    qc.setToolTip(txt)

                if ti.order == 0:
                    qc.set_color_shadow()

        if overall:
            i, p = self.game.take_player()
            self.table_label.setText(f'Взял: {p.name}')
            self.next_button.show()

    def clear_table(self):
        """ Очистка всех элементов с центральной обласи, где отображаются карты, которыми походили """

        if self.table_label:
            self.table_label.setText(None)

        if self.next_button:
            self.next_button.hide()

        for k in self.table:
            if isinstance(self.table[k], QCard):
                self.scene.removeItem(self.table[k])

        self.table = {}

    def draw_order(self):
        """ Отрисовка заказа игроков """

        n = 0

        for i, p in enumerate(self.players):
            if p.order > -1:
                self.labels[i]['order'].setText('{0}{1}'.format(p.order, '*' if p.order_is_dark else ''))
                n += p.order

        if len([p for p in self.players if p.order > -1]) == len(self.players):
            diff = n - self.game.current_deal().cards
            self.order_info_label.setStyleSheet('QLabel {color: %s}' % '{0}'.format('Lime' if diff < 0 else 'OrangeRed'))
            self.order_info_label.setText('{0} {1}'.format('Перебор ' if diff < 0 else 'Недобор', abs(diff)))
        else:
            self.order_info_label.setText(None)

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

    def hide_order_and_take(self):
        """ Убрать информацию о заказе и взятке у игроков """

        for i, p in enumerate(self.players):
            self.labels[i]['order'].setText(None)
            self.labels[i]['take'].setText(None)

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
        bx = round(const.AREA_SIZE[0] / 2) - round((55 * coef) / 2) - 20
        x = bx

        for i in range(self.game.current_deal().cards + 1):
            if i == cols + 1:
                x = bx

            x = x + 55
            if i <= cols:
                y = round(const.AREA_SIZE[1] / 2)
            else:
                y = round(const.AREA_SIZE[1] / 2) + 60

            b, s = self.game.check_order(i, self.order_dark or False)
            btn = self.add_button(lambda state, z=i: self.order_btn_click(z), f'{i}', (50, 50), (x, y),
                                   16, 65, 'DarkGreen' if b else 'Gray', 'Lime' if b else 'DimGray')

            btn.setDisabled(not b)
            btn.setToolTip(s)
            self.buttons.append(btn)

    def show_joker_action_buttons(self):
        """ Показ кнопок выбора действия джокером """

        self.table_label.setText('Ход джокером. Выбери действие')

        if not self.game.table():
            # если мой ход первый - показать еще вариант "по старшей"
            self.ja_take_by_btn.show()

        self.ja_take_btn.show()
        self.ja_give_btn.show()

    def show_ja_lear_buttons(self):
        """ Показ кнопок выбора масти джокера """

        self.table_label.setText('Ход джокером. Выбери масть')

        for btn in self.ja_lear_buttons:
            btn.show()

    def fill_game_table(self):
        """ Заливает таблицу хода игры """

        recs = self.game.get_record()

        for i, rec in enumerate(recs[1:]):
            if rec == recs[-1]:
                if self.game.status() != core_const.EXT_STATE_ROUND_PAUSE or (
                    self.game.status() == core_const.EXT_STATE_ROUND_PAUSE and not self.is_new_round):
                    self.add_table_row(rec, self.game.get_deals()[i])
            else:
                self.add_table_row(rec, self.game.get_deals()[i])

    def add_table_row(self, record, deal=None):
        """
        Добавляет в конец строку к таблице хода игры

        :param record: строка с результатами раунда, которую надо добавить
        :param deal: раздача, связанная с добавляемой строкой. Если нет - берет текущую раздачу игры
        """

        row = []
        colors = ['Purple']
        max_scores = max([p.total_scores for p in self.players])
        if not deal:
            deal = self.game.current_deal()

        if deal.type_ < 3:
            row.append(f'по {deal.cards}')
        else:
            row.append(core_const.DEAL_NAMES[deal.type_][0])

        for p in self.players:
            colors.append('aqua')
            order = int(record[p.uid]['order'].split('*')[0])
            scores = int(record[p.uid]['scores'].split(' ')[0])

            if record[p.uid]['take'] < order or deal.type_ == core_const.DEAL_MIZER:
                colors.append('OrangeRed')
            elif record[p.uid]['take'] > order and deal.type_ != core_const.DEAL_GOLD:
                colors.append('Fuchsia')
            else:
                colors.append('Lime')

            if scores < 0:
                colors.append('OrangeRed')
            elif scores > 9:
                colors.append('Lime')
            else:
                colors.append('Fuchsia')

            if record[p.uid]['total'] < 0:
                colors.append('OrangeRed')
            elif record[p.uid]['total'] >= max_scores :
                colors.append('Lime')
            else:
                colors.append('aqua')

            for k in record[p.uid]:
                if k == 'order':
                    row.append(record[p.uid][k].replace('-1', '-'))
                else:
                    row.append(record[p.uid][k])

        self.game_table.add_row(row, colors)

    def show_round_results(self):
        """ Показ результатов раунда """

        rec = self.game.get_record()
        self.add_table_row(rec[-1])
        max_scores = max([p.total_scores for p in self.players])
        d = self.game.current_deal()

        for i, player in enumerate(self.players):
            tmpl = ''.join(('{player}<br>{order} | ',
                            '<span style="color: {take_color}">{take}</span> | ',
                            '<span style="color: {scores_color}">{scores}</span><br>',
                            '<span style="color: {total_color}"><b>{total}</b></span>'))

            keys = {k: v for k, v in rec[-1][player.uid].items()}
            keys['player'] = player.name

            order = int(keys['order'].split('*')[0])
            scores = int(keys['scores'].split(' ')[0])
            keys['order'] = keys['order'].replace('-1', '-')

            if keys['take'] < order or d.type_ == core_const.DEAL_MIZER:
                keys['take_color'] = 'OrangeRed'
            elif keys['take'] > order and d.type_ != core_const.DEAL_GOLD:
                keys['take_color'] = 'Fuchsia'
            else:
                keys['take_color'] = 'Lime'

            if scores < 0:
                keys['scores_color'] = 'OrangeRed'
            elif scores > 9:
                keys['scores_color'] = 'Lime'
            else:
                keys['scores_color'] = 'Fuchsia'

            if keys['total'] < 0:
                keys['total_color'] = 'OrangeRed'
            elif keys['total'] >= max_scores:
                keys['total_color'] = 'Lime'
            else:
                keys['total_color'] = 'aqua'

            self.round_result_labels[i].setText(tmpl.format(**keys))
            self.round_result_labels[i].show()

        self.table_label.setText(None)
        self.next_button.show()

    def hide_round_results(self):
        """ Скрыть итоги раунта """

        for lb in self.round_result_labels:
            lb.setText(None)
            lb.hide()

    def show_game_results(self):
        """ Показ результатов игры """

        pos = (round(const.AREA_SIZE[0] / 2) - round(const.TABLE_AREA_SIZE[0] / 2) + 50,
               round(const.AREA_SIZE[1] / 2) - round(const.TABLE_AREA_SIZE[1] / 2) + 30)

        self.set_text('-= Итоги игры =-', pos, Qt.cyan, 18, 65)
        winner = max([p for p in self.game.players], key=lambda o: o.total_money)

        x, y = pos[0], pos[1] + 20

        for i, p in enumerate(self.game.players, 1):
            money = '{0:.2f}'.format(p.total_money)
            rub, kop = money.split('.')
            self.set_text(f'{p.name}:    {p.total_scores} :: {rub} руб {kop} коп', (x, y + i * 30),
                          Qt.green if p == winner else Qt.yellow, 18, 65)

        y = y + len(self.game.players) * 30 + 60
        self.set_text(f'Победил {winner.name}', (x, y), Qt.green, 18, 65)
        self.set_text(random.choice(const.CONGRATULATIONS), (x, y + 60), Qt.magenta, 18, 65)

    def clear_buttons(self):
        """ Убирает все кнопки с центральной области """

        for btn in self.buttons:
            self.remove_widget(btn)

        self.buttons = []

        if self.table_label:
            self.table_label.setText(None)

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

    def card_click(self, card, joker_handling=True):
        """
        Обработка нажатия на карты

        :param QCard card: карта, на которую нажали
        :param joker_handling: если карта джокер - показать кнопки действий джокером, или среагировать как на обычную карту
            нужно для того, чтоб после выбора действий джокером продолжить дальше
        """

        c = card.card
        p = card.player

        if self.started() and p and not p.is_robot and self.game.status() == core_const.EXT_STATE_WALKS and not self.game.is_bet():
            try:
                if c.joker and joker_handling:
                    self.joker_walk_card = card
                    self.show_joker_action_buttons()
                    return
                else:
                    self.game.do_walk(p.cards.index(c))
                    self.game.give_walk()
                    self.game.next()
                    self.joker_walk_card = None
            except helpers.GameException as e:
                QMessageBox.warning(self, 'Ход', f'{e}', QMessageBox.Ok)

            self.next()

    def joker_action_btn_click(self, action):
        """ Нажатие кнопки выбора действия джокером """

        self.ja_take_by_btn.hide()
        self.ja_take_btn.hide()
        self.ja_give_btn.hide()

        card = self.joker_walk_card.card
        card.joker_action = action

        if not self.game.table():
            # если мой ход первый: если скидываю и в настройках игры установлено, что Джокер играет по номиналу,
            # то масть будет мастью реальной карты - т.е. пика (джокер - это 7 пика);
            # в остальных случаях надо выбрать, с какой масти заходить
            if action == core_const.JOKER_GIVE and self.game.joker_give_at_par:
                l = card.lear
            else:
                self.show_ja_lear_buttons()
                return
        else:
            # если я покрываю джокером: если я забираю - надо установить или козырную масть или масть той карты,
            # с которой зашли;
            # если скидываю - то или по номиналу или масть карты, с которой зашли
            ftbl = self.game.lap_players_order(by_table=True)[0]
            if action == core_const.JOKER_TAKE:
                l = self.game.trump()[0] if self.game.trump()[0] != core_const.LEAR_NOTHING else self.game.table()[ftbl[1]].card.lear
            else:
                l = card.lear if self.game.joker_give_at_par else self.game.table()[ftbl[1]].card.lear

        card.joker_lear = l
        self.card_click(self.joker_walk_card, False)

    def ja_select_lear_btn_click(self, lear):
        """ Нажатие кнопки выбора масти джокера """

        for btn in self.ja_lear_buttons:
            btn.hide()

        self.joker_walk_card.card.joker_lear = lear
        self.card_click(self.joker_walk_card, False)

    def next_button_click(self):
        """ Нажатие кнопки Далее """

        self.next_button.hide()
        self.game.next()
        self.next()

    def show_statistics_grid(self):
        """ Показ таблицы хода игры """

        if self.can_show_results:
            self.game_table.setWindowTitle('Итоги игры')
        self.game_table.move(self.pos())
        self.game_table.show()

    def get_face_positions(self):
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

    def get_area_positions(self):
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

    def get_label_offsets(self):
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

    def get_table_offsets(self):
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

    def get_round_info_positions(self):
        """ Позиции расположения лебелов с результатами игры """

        x, y = round(const.AREA_SIZE[0] / 2) + 60, round(const.AREA_SIZE[1] / 2)

        if len(self.players) == 4:
            return (
                (x - round(const.TABLE_AREA_SIZE[0] / 2), y + round(const.TABLE_AREA_SIZE[0] / 2) - 100),  # позиция человека, низ центр
                (x - round(const.TABLE_AREA_SIZE[0] / 2), y + 10),  # лево центр
                (x - round(const.TABLE_AREA_SIZE[0] / 2) + 120, y - round(const.TABLE_AREA_SIZE[0] / 2) + 150),  # верх центр
                (x - 20, y + 10)  # право центр
            )
        else:
            return (
                (x - round(const.TABLE_AREA_SIZE[0] / 2), y + round(const.TABLE_AREA_SIZE[0] / 2) - 100),  # позиция человека, низ центр
                (x - round(const.TABLE_AREA_SIZE[0] / 2), y - round(const.TABLE_AREA_SIZE[0] / 2) + 150),  # левый верхний угол
                (x - 20, y - round(const.TABLE_AREA_SIZE[0] / 2) + 150)  # правый верхний угол
            )

    def get_round_info_aligns(self):
        """ Выравнивание текста в лебелах с результатами игры """

        if len(self.players) == 4:
            return Qt.AlignHCenter, Qt.AlignLeft, Qt.AlignHCenter, Qt.AlignRight
        else:
            return Qt.AlignHCenter, Qt.AlignLeft, Qt.AlignRight

    def get_joker_info(self, card):
        """ Представление информации о действии джокером в читабельном виде """

        if card.joker:
            clr = 'red' if card.joker_lear > 1 else 'black'
            tmpl = '<span style="color:{0}">{1}</span>'.format(clr, '{0}')

            if card.joker_action == core_const.JOKER_TAKE:
                s, l = 'самая старшая', tmpl.format(core_const.LEAR_SYMBOLS[card.joker_lear])
            elif card.joker_action == core_const.JOKER_TAKE_BY_MAX:
                s, l = 'по старшим', tmpl.format(core_const.LEAR_SYMBOLS[card.joker_lear])
            elif card.joker_action == core_const.JOKER_GIVE:
                s, l = 'самая младшая', tmpl.format(core_const.LEAR_SYMBOLS[card.joker_lear])\
                    if not self.game.joker_give_at_par else f'{card}'
            else:
                s, l = None, None

            return '{0} {1}'.format(s, l)
        else:
            return ''

    def get_profile_dir(self):
        """ возвращает путь к папке активного профиля """

        return f'{const.PROFILES_DIR}/{self.params.user}'

    def load_save_file(self, filename):
        """ Грузит файл сохранения, возвращает загруженные данные в виде 2-х блоков: состояние главного потока и дамп ядра """

        with open(filename, mode='rb') as f:
            raw = f.read()

        t, e = raw.split(b'\0x4')
        t = json.loads(t.decode('utf-8'))
        e = pickle.loads(e, encoding='utf-8')

        return t, e

    def write_save_file(self, filename, opts):
        """ Запись данных сохранения в файл """

        t = json.dumps(opts).encode('utf-8')
        e = pickle.dumps(self.game)

        raw = b'\0x4'.join((t, e))

        if not os.path.isdir(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])

        with open(filename, 'wb') as f:
            f.write(raw)

    def save_exists(self):
        """ Проверяет, есть ли сохранение для активного профиля и возвращает путь к файлу сохранения """

        fn = f'{self.get_profile_dir()}/save/auto.psg'

        if os.path.exists(fn):
            return True, fn
        else:
            return False, None

    def save_params(self):
        """ Сохранение параметров """

        if not os.path.isdir(const.APP_DATA_DIR):
            os.makedirs(const.APP_DATA_DIR)

        self.params.save(const.PARAMS_FILE)
        self.profiles.save(const.PROFILES_FILE)
        self.save_profile_options()

    def save_profile_options(self):
        """ Сохранение параметров текущего профиля """

        if self.params.user and self.curr_profile:
            fn = f'{self.get_profile_dir()}/options.json'

            if not os.path.isdir(os.path.split(fn)[0]):
                os.makedirs(os.path.split(fn)[0])

            self.options.save(fn)
