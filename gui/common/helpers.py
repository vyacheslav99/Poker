from PyQt5.QtWidgets import QMenuBar, QActionGroup, QAction


class MenuActions:

    menu_file: QMenuBar
    start_actn: QAction
    throw_actn: QAction
    statistics_actn: QAction
    svc_actn: QAction

    menu_user: QMenuBar
    login_actn: QAction
    registration_actn: QAction
    edit_users_actn: QAction
    profiles_group: QActionGroup
    logout_actn: QAction
