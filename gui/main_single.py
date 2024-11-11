import os
import random
import pickle
import json

from datetime import datetime, timedelta

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from core import const as core_const, engine
from models.params import Options, RobotStatItem

from gui import const, utils
from gui.main_base import MainWnd
from gui.service_info import ServiceInfoDialog
from gui.players_dlg import PlayersDialog
from gui.agreements_dlg import AgreementsDialog
from gui.profiles_dlg import ProfilesDialog


class SinglePlayerMainWnd(MainWnd):

    def __init__(self, app, *args):
        super().__init__(app, *args)

        self.__dev_mode = '--dev_mode' in args

        if os.path.exists(const.PARAMS_FILE):
            self.params.load(const.PARAMS_FILE)

        if os.path.exists(const.PROFILES_FILE):
            self.profiles.load(const.PROFILES_FILE)

        self.svc_actn = None
        self.service_wnd = None

        self.init_profile()
        self.apply_decoration()
        self.init_menu_actions()
        self.show()

    def init_menu_actions(self):
        super().init_menu_actions()

        if self.__dev_mode:
            self.svc_actn = QAction(QIcon(f'{const.RES_DIR}/svc.ico'), 'Служебная информация', self)
            self.svc_actn.setShortcut('F9')
            self.svc_actn.setStatusTip('Показать окно со служебной информацией')
            self.svc_actn.triggered.connect(self.show_service_window)
            self.file_menu.insertAction(self.file_menu.actions()[5], self.svc_actn)

    def refresh_menu_actions(self):
        super().refresh_menu_actions()

        if self.svc_actn:
            self.svc_actn.setEnabled(self.started())

        if self.started():
            self.start_actn.setText('Отложить партию')
            self.start_actn.setStatusTip('Отложить партию.\nВы сможете продолжить ее позднее')
        else:
            if self.save_exists()[0]:
                self.start_actn.setText('Продолжить партию')
                self.start_actn.setStatusTip('Вернуться к отложенной партии')
            else:
                self.start_actn.setText('Новая партия')
                self.start_actn.setStatusTip('Начать новую партию')

    def show_service_window(self):
        if self.__dev_mode and self.started():
            if not self.service_wnd:
                self.service_wnd = ServiceInfoDialog(self)

            self.service_wnd.players = self.players
            self.service_wnd.show()

    def show_profiles_dlg(self):
        dlg = ProfilesDialog(self, self.profiles, self.params.user)

        try:
            # в форму передаем сам объект Profiles, сохраняем (или отменяем) изменения в каждом профиле прям там,
            # так что после закрытия диалога в профилях уже все изменения есть, остается только сохранить в файл
            curr_changed = dlg.exec()

            if curr_changed:
                self.set_profile(self.params.user)

            self.save_params()

            if curr_changed and self.started():
                self.restart_game()
        finally:
            dlg.destroy()

    def change_profile_action(self, action):
        new_uid = action.data()

        if self.curr_profile is not None and self.curr_profile.uid != new_uid:
            self.set_profile(new_uid)
            self.save_params()

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
        self.set_status_message(self.curr_profile.name, 0)

        if os.path.exists(f'{self.get_profile_dir()}/options.json'):
            self.options = Options(filename=f'{self.get_profile_dir()}/options.json')
        else:
            self.options = Options()

    def on_throw_action(self):
        """ Обработчик меню Бросить партию """

        res = QMessageBox.question(self, 'Подтверждение',
                                   'Хотите бросить партию? Продолжить ее уже будет невозможно.\n',
                                   QMessageBox.Yes | QMessageBox.No)

        if res == QMessageBox.No:
            return

        if self.started():
            self.stop_game(core_const.GAME_STOP_THROW)
            self.clear_save()

        self.refresh_menu_actions()

    def start_game(self):
        """ Старт игры - инициализация игры и показ игрового поля """

        if self.save_exists()[0]:
            return self.load_game()

        self.stop_game(core_const.GAME_STOP_DEFER)

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
            # подгрузим компьютерным игрокам их статистику
            if p.is_robot and p.name in self.params.robots_stat:
                p.from_dict(self.params.robots_stat[p.name])

        self.options.players_cnt = len(self.players)
        self.game = engine.Engine(self.players, allow_no_human=False, **self.options.as_dict())
        self.game.start()

        # И поехала игра
        self._started = True
        self._prv_game_time = None
        self._start_time = datetime.now()
        self.is_new_round = True
        self._timer = utils.IntervalTimer(1.0, self.display_game_time)

        if self.params.show_bikes:
            self._bike_timer = utils.IntervalTimer(float(random.randint(*const.BIKE_TIMER_INTERVAL)), self.show_bike)

        self.init_game_table()
        self.next()

    def load_game(self):
        """ Загрузка сохраненной игры """

        self.stop_game(core_const.GAME_STOP_DEFER)
        self.can_show_results = False
        b, fn = self.save_exists()

        if not b:
            return

        mt, self.game = self.load_save_file(fn)

        # устанавливаем игровые переменные модуля
        self.order_dark = mt['order_dark']
        self.joker_walk_card = mt['joker_walk_card']
        self.is_new_lap = mt['is_new_lap']
        self.is_new_round = mt['is_new_round']
        self._prv_game_time = timedelta(seconds=mt['game_time'] or 0.0)

        self.players = self.game.players
        for i, p in enumerate(self.players):
            # загруженного игрока человека надо подменить на текущего, чтобы актуализировать его данные
            # (по сути это он и есть, но физически объекты уже разные)
            if p.uid == self.params.user:
                user = self.profiles.get(self.params.user)
                user.assign_game_variables(p)
                self.players[i] = user
                break

        self._started = True
        self._start_time = datetime.now()
        self._timer = utils.IntervalTimer(1.0, self.display_game_time)

        if self.params.show_bikes:
            self._bike_timer = utils.IntervalTimer(float(random.randint(*const.BIKE_TIMER_INTERVAL)), self.show_bike)

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
            'is_new_round': self.is_new_round,
            'game_time': self.game_time().total_seconds()
        }

        fn = f'{self.get_profile_dir()}/save/auto.psg'
        self.write_save_file(fn, o)

    def stop_game(self, flag=None):
        """ Остановить игру, очистить игровое поле """

        if self.service_wnd:
            self.service_wnd.hide()

        if self.game and self.game.started():
            self.game.stop(flag)

        if self._timer and self._timer.active():
            self._timer.stop()

        if self._bike_timer and self._bike_timer.active():
            self._bike_timer.stop()

        self._started = False
        self._start_time = None
        self.players = []
        self.clear()

    def clear_save(self):
        """ Удаляет ненужный файл автосохранения """

        b, fn = self.save_exists()

        if b:
            os.unlink(fn)

    def next(self):
        """ Обработка игрового цикла """

        if not self.game.started():
            if self.can_show_results:
                # сохраняем статистику компьютерных игроков
                for p in self.players:
                    if p.is_robot:
                        self.params.robots_stat[p.name] = RobotStatItem(**p.as_dict()).as_dict()

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
                if (self.game.dark_allowed and d.type_ not in (core_const.DEAL_DARK, core_const.DEAL_BROW)
                    and self.order_dark is None):
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

    def get_profile_dir(self):
        """ возвращает путь к папке активного профиля """

        return f'{const.PROFILES_DIR}/{self.params.user}'

    def load_save_file(self, filename):
        """
        Грузит файл сохранения, возвращает загруженные данные в виде 2-х блоков: состояние главного потока и дамп ядра
        """

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

    def reset_statistics(self):
        self.params.robots_stat = {}

        for p in self.profiles.profiles:
            p.reset_statistics()

    def on_reset_stat_click(self):
        res = QMessageBox.question(
            self._stat_wnd, 'Подтверждение', 'Действительно сбросить все результаты???\n',
            QMessageBox.Yes | QMessageBox.No
        )

        if res == QMessageBox.No:
            return

        self.reset_statistics()
        self._stat_wnd.set_data(self.profiles, self.params.robots_stat,
                                self.curr_profile.uid if self.curr_profile else None)

        QMessageBox.information(
            self._stat_wnd, 'Сообщение', 'Поздравляю! Все похерено успешно', QMessageBox.Ok
        )
