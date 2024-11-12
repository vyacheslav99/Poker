import os

from PyQt5.QtWidgets import *

from models.params import Options
from gui.common import const
from gui.common.client import GameServerClient, RequestException
from gui.main_base import MainWnd
from models.player import Player


class MultiPlayerMainWnd(MainWnd):

    def __init__(self, app, *args):
        super().__init__(app, *args)

        self.load_params()
        self.game_server_cli: GameServerClient = GameServerClient(self.params.server)

        if os.path.exists(const.PROFILES_NET_FILE):
            self.profiles.load(const.PROFILES_NET_FILE)

        self.init_profile()
        self.apply_decoration()
        self.init_menu_actions()
        self.show()

    def show_profiles_dlg(self):
        pass

    def authorize(self, username: str, password: str) -> Player:
        try:
            self.game_server_cli.authorize_safe(username, password)
            return self.game_server_cli.get_user()
        except RequestException as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка авторизации:\n\n{str(e)}')

    def init_profile(self):
        """ Инициализация текущего профиля """

        if self.profiles.count() == 0:
            # todo: тут будет окно авторизации/регистрации, а пока закостылим так
            self.profiles.set_profile(self.authorize('vika', 'zadnitsa'))
            self.params.user = self.profiles.profiles[0].uid

        if not self.params.user:
            self.params.user = self.profiles.profiles[0].uid

        self.set_profile(self.params.user)

    def set_profile(self, uid):
        """ Смена текущего профиля """

        profile = self.profiles.get(uid)

        if not profile:
            return

        self.params.user = uid
        self.game_server_cli.token = profile.password

        if os.path.exists(f'{self.get_profile_dir()}/options.json'):
            self.options = Options(filename=f'{self.get_profile_dir()}/options.json')
        else:
            self.options = Options()

        try:
            profile = self.game_server_cli.get_user()
            # todo: метод клиента пока не реализован, чтоб все не херить, пока закомментировано
            # self.options = self.game_server_cli.get_game_agreements()
            self.load_params(remote=True)
        except RequestException as e:
            QMessageBox.warning(
                self, 'Ошибка',
                f'Не удалось загрузить профиль с сервера! Ошибка:\n{str(e)}\n\n'
                f'Был загружен профиль из локального кэша'
            )

        self.curr_profile = profile
        self.set_status_message(self.curr_profile.name, 0)

    def save_profile_options(self, local_only: bool = False):
        """ Сохранение параметров текущего профиля """

        super().save_profile_options()

        if self.params.user and self.curr_profile:
            if not local_only:
                try:
                    # todo: метод клиента пока не реализован, чтоб все не херить, пока закомментировано
                    # self.game_server_cli.set_game_agreements(self.options)
                    pass
                except RequestException as e:
                    QMessageBox.warning(
                        self, 'Ошибка',
                        f'Не удалось сохранить настройки на сервере! Ошибка:\n{str(e)}\n\n'
                        f'Настройки сохранены в локальный кэш'
                    )

    def load_params(self, remote: bool = False):
        """ Загрузка параметров """

        if remote:
            try:
                # todo: метод клиента пока не реализован, чтоб все не херить, пока закомментировано
                # self.params.set(**self.game_cli.get_params().as_dict())
                pass
            except RequestException as e:
                QMessageBox.warning(
                    self, 'Ошибка',
                    f'Не удалось загрузить настройки с сервера! Ошибка:\n{str(e)}\n\n'
                    f'Были загружены настройки из локального кэша'
                )
        else:
            if os.path.exists(const.PARAMS_NET_FILE):
                self.params.load(const.PARAMS_NET_FILE)
            elif os.path.exists(const.PARAMS_FILE):
                # сетевой модуль еще не инициализировался - скопируем настройки из синглплеера, если они есть
                self.params.load(const.PARAMS_FILE)
                self.params.user = None

    def save_params(self, local_only: bool = False):
        """ Сохранение параметров """

        if not os.path.isdir(const.APP_DATA_DIR):
            os.makedirs(const.APP_DATA_DIR)

        self.params.save(const.PARAMS_NET_FILE)
        self.profiles.save(const.PROFILES_NET_FILE)
        self.save_profile_options(local_only=local_only)

        if not local_only:
            try:
                # todo: метод клиента пока не реализован, чтоб все не херить, пока закомментировано
                # self.game_server_cli.set_params(self.params)
                pass
            except RequestException as e:
                QMessageBox.warning(
                    self, 'Ошибка',
                    f'Не удалось сохранить настройки на сервере! Ошибка:\n{str(e)}\n\n'
                    f'Настройки сохранены в локальный кэш'
                )

    def on_throw_action(self):
        pass

    def start_game(self):
        pass

    def stop_game(self, flag=None):
        pass

    def next(self):
        pass

    def on_reset_stat_click(self):
        # наверное тут будет обнуляться собственная статистика текущего игрока на сервере
        pass
