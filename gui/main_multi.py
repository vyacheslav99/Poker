import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from models.params import Options
from gui.common import const
from gui.common.client import GameServerClient, ClientException, RequestException
from gui.main_base import MainWnd


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

    def handle_client_exception(
        self, err: Exception, before_msg: str = None, after_msg: str = None, goto_authorization: bool = True
    ):
        can_authorize = False

        if isinstance(err, ClientException):
            can_authorize = err.status_code == 401
            msg = err.message
        else:
            msg = str(err)

        parts = []

        if before_msg:
            parts.append(before_msg)
        if msg:
            parts.append(msg)
        if after_msg:
            parts.append(after_msg)

        QMessageBox.critical(self, 'Ошибка', '\n'.join(parts))

        if can_authorize and goto_authorization:
            self.show_profiles_dlg()

    def init_menu_actions(self):
        super().init_menu_actions()

        self.menu_actions.registration_actn = QAction(QIcon(f'{const.RES_DIR}/player.ico'), 'Регистрация', self)
        self.menu_actions.registration_actn.setStatusTip('Регистрация нового пользователя')
        self.menu_actions.registration_actn.triggered.connect(self.show_registration_dlg)
        self.menu_actions.menu_user.insertAction(
            self.menu_actions.menu_user.actions()[0], self.menu_actions.registration_actn
        )

        self.menu_actions.login_actn = QAction(QIcon(f'{const.RES_DIR}/login.png'), 'Вход', self)
        self.menu_actions.login_actn.setStatusTip('Авторизация')
        self.menu_actions.login_actn.triggered.connect(self.show_login_dlg)
        self.menu_actions.menu_user.insertAction(self.menu_actions.registration_actn, self.menu_actions.login_actn)

        self.menu_actions.menu_user.addSeparator()
        self.menu_actions.logout_actn = QAction(QIcon(f'{const.RES_DIR}/exit.ico'), 'Выход', self)
        self.menu_actions.logout_actn.setStatusTip('Разлогиниться текущим пользователем')
        self.menu_actions.logout_actn.triggered.connect(self.on_logout_action)
        self.menu_actions.menu_user.addAction(self.menu_actions.logout_actn)

    def show_login_dlg(self):
        """ Форма авторизации """

        # todo: тут будет окно авторизации/регистрации, а пока закостылим так
        QMessageBox.information(
            self, 'Вход', 'Форма входа пока не реализована, закостылен вход пользователем < vika >'
        )

        try:
            self.game_server_cli.authorize_safe('vika', 'zadnitsa')
            user = self.game_server_cli.get_user()
            self.profiles.set_profile(user)
            self.params.user = user.uid
        except Exception as err:
            self.handle_client_exception(err, goto_authorization=False)

    def show_registration_dlg(self):
        """ Форма регистрации пользователя """

        # todo: Реализовать
        QMessageBox.information(self, 'Регистрация', 'Форма регистрации пока не реализована')

    def show_profiles_dlg(self):
        """ Форма управления пользователями """

        # todo: Реализовать, тут будет отдельная форма, не та, что в синглплеере
        QMessageBox.information(
            self, 'Профиль', 'Форма редактирования профиля для мультиплеера пока не реализована'
        )

    def on_logout_action(self):
        """ Выход (разлогиниться) текущим пользователем """

        res = QMessageBox.question(
            self, 'Выход', f'Действительно выйти пользователем < {self.curr_profile.login} > ?',
            QMessageBox.Yes | QMessageBox.No
        )

        if res == QMessageBox.No:
            return

        # todo: Реализовать процесс выхода

    def init_profile(self):
        """ Инициализация текущего профиля """

        if self.profiles.count() == 0:
            self.show_profiles_dlg()

        if self.profiles.count() == 0:
            return

        if not self.params.user:
            self.params.user = self.profiles.profiles[0].uid

        self.set_profile(self.params.user)

    def set_profile(self, uid):
        """ Смена текущего профиля """

        user = self.profiles.get(uid)

        if not user:
            self.params.user = None
            return

        self.params.user = uid
        self.game_server_cli.token = user.password

        if os.path.exists(f'{self.get_profile_dir()}/options.json'):
            self.options = Options(filename=f'{self.get_profile_dir()}/options.json')
        else:
            self.options = Options()

        try:
            user = self.game_server_cli.get_user()

            if user.avatar:
                try:
                    self.game_server_cli.download_avatar(user.avatar, os.path.join(self.get_profile_dir(), user.avatar))
                except RequestException:
                    pass

            self.profiles.set_profile(user)
            self.load_params(remote=True)
        except RequestException as err:
            self.handle_client_exception(
                err,
                before_msg='Не удалось загрузить профиль с сервера! Ошибка:',
                after_msg='Восстановлен профиль из локального кэша'
            )

        self.curr_profile = user
        self.set_status_message(self.curr_profile.name, 0)

    def load_params(self, remote: bool = False):
        """ Загрузка параметров """

        if remote:
            try:
                self.params.set(**self.game_server_cli.get_params())
                self.options.set(**self.game_server_cli.get_game_options())
            except RequestException as err:
                self.handle_client_exception(
                    err,
                    before_msg='Не удалось загрузить настройки с сервера! Ошибка:',
                    after_msg='Восстановлены настройки из локального кэша'
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
        self.save_profile_options()

        if not local_only:
            try:
                self.game_server_cli.set_params(self.params)
                self.game_server_cli.set_game_options(self.options)
            except RequestException as err:
                self.handle_client_exception(
                    err,
                    before_msg='Не удалось сохранить настройки на сервере! Ошибка:',
                    after_msg='Настройки сохранены в локальный кэш'
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
