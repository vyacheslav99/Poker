import os
import shutil

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from models.params import Options
from gui.common import const
from gui.common.utils import handle_client_exception
from gui.common.client import GameServerClient, RequestException
from gui.main_base import MainWnd
from gui.windows.login_dlg import LoginDialog
from gui.windows.registration_dlg import RegistrationDialog
from gui.windows.profiles_net_dlg import ProfilesNetDialog


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
        self.refresh_menu_actions()
        self.show()

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

    def refresh_menu_actions(self):
        """ Акуализация состояния игрового меню """

        super().refresh_menu_actions()

        self.menu_actions.edit_users_actn.setEnabled(self.curr_profile is not None)
        self.menu_actions.logout_actn.setEnabled(self.curr_profile is not None)
        self.menu_actions.edit_users_actn.setEnabled(not self.started() and self.profiles.count() > 0)

    def show_settings_dlg(self):
        super().show_settings_dlg()

        if self.params.server != self.game_server_cli.base_host:
            self.game_server_cli.base_host = self.params.server

    def show_login_dlg(self, set_login: str = None):
        """ Форма авторизации """

        login_dlg = LoginDialog(self, login=set_login)
        result = login_dlg.exec()
        if result == 0:
            login_dlg.destroy()
            return

        login = login_dlg.get_login()
        password = login_dlg.get_password()
        login_dlg.destroy()

        if not login or not password:
            return

        try:
            self.game_server_cli.authorize_safe(login, password)
            user = self.game_server_cli.get_user()
            self.profiles.set_profile(user)
            self.set_profile(user.uid)
            self.refresh_menu_actions()
        except Exception as err:
            if handle_client_exception(self, err):
                self.show_login_dlg(set_login=login)

    def show_registration_dlg(self):
        """ Форма регистрации пользователя """

        register_dlg = RegistrationDialog(self)
        result = register_dlg.exec()
        if result == 0:
            register_dlg.destroy()
            return

        login = register_dlg.get_login()
        password = register_dlg.get_password()
        register_dlg.destroy()

        if not login or not password:
            return

        try:
            user = self.game_server_cli.registration(login, password)
            user.password = self.game_server_cli.authorize_safe(login, password)
            self.profiles.set_profile(user)
            self.set_profile(user.uid)
            self.refresh_menu_actions()
        except Exception as err:
            handle_client_exception(self, err)

    def show_profiles_dlg(self):
        """ Форма изменения профиля пользователя """

        dlg = ProfilesNetDialog(self, self.profiles, self.params.user)

        try:
            # Изменения на сервер отправляем сразу из формы
            # Локально изменения сохраняются сразу в объекте Profiles
            # поэтому после закрытия диалога в профилях уже все изменения есть, остается только сохранить в файл
            dlg.exec()
            self.profiles.save(const.PROFILES_NET_FILE)

            if not self.profiles.get(self.params.user):
                # если текущий профиль удален (из списка ну и вобще, в данном случае не важно)
                self.params.user = None
                self.init_profile()

            self.refresh_menu_actions()
            self.set_status_message(self.curr_profile.name if self.curr_profile else '', 0)
        finally:
            dlg.destroy()

    def on_logout_action(self):
        """ Выход (разлогиниться) текущим пользователем """

        if not self.curr_profile:
            QMessageBox.information(self, 'Выход', 'Собственно ты и так не авторизован...')
            return

        res = QMessageBox.question(
            self, 'Выход',
            f'Выйти пользователем < {self.curr_profile.login} ({self.curr_profile.name}) > ?',
            QMessageBox.Yes | QMessageBox.No
        )

        if res == QMessageBox.No:
            return

        try:
            self.game_server_cli.logout()
        except Exception as err:
            handle_client_exception(self, err)

        fldr = self.get_profile_dir()
        if os.path.isdir(fldr):
            shutil.rmtree(fldr)

        self.profiles.delete(self.params.user)
        self.params.user = None
        self.init_profile()
        self.refresh_menu_actions()

    def init_profile(self):
        """ Инициализация текущего профиля """

        if self.profiles.count() > 0 and not self.params.user:
            self.params.user = self.profiles.profiles[0].uid

        self.set_profile(self.params.user)

    def set_profile(self, uid):
        """ Смена текущего профиля """

        user = self.profiles.get(uid)

        if not user:
            self.params.user = None
            self.game_server_cli.token = None
        else:
            self.params.user = uid
            self.game_server_cli.token = user.password

        if user and not os.path.exists(self.get_profile_dir()):
            os.makedirs(self.get_profile_dir(), exist_ok=True)

        if user and os.path.exists(f'{self.get_profile_dir()}/options.json'):
            self.options = Options(filename=f'{self.get_profile_dir()}/options.json')
        else:
            self.options = Options()

        if user:
            try:
                user = self.game_server_cli.get_user()
                self.profiles.set_profile(user)

                if user.avatar:
                    try:
                        self.game_server_cli.download_avatar(
                            user.avatar, os.path.join(self.get_profile_dir(), user.avatar)
                        )
                    except RequestException:
                        pass
            except RequestException as err:
                handle_client_exception(
                    self, err,
                    before_msg='Не удалось загрузить профиль с сервера! Ошибка:',
                    after_msg='Восстановлен профиль из локального кэша'
                )
        else:
            self.save_params(local_only=True)

        self.curr_profile = user
        self.load_params(remote=True)
        self.apply_decoration()
        self.set_status_message(self.curr_profile.name if self.curr_profile else '', 0)

    def load_params(self, remote: bool = False):
        """ Загрузка параметров """

        if remote and self.curr_profile:
            try:
                self.params.set(**self.game_server_cli.get_params())
                self.options.set(**self.game_server_cli.get_game_options())
            except RequestException as err:
                handle_client_exception(
                    self, err,
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

        if not local_only and self.curr_profile:
            try:
                self.game_server_cli.set_params(self.params)
                self.game_server_cli.set_game_options(self.options)
            except RequestException as err:
                handle_client_exception(
                    self, err,
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

    def allow_change_profile_in_settings(self) -> bool:
        return False
