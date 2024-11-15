from PyQt5.QtWidgets import QMenuBar, QActionGroup, QAction, QMenu


class MenuActions:

    menu_file: QMenuBar = None
    start_actn: QAction = None
    throw_actn: QAction = None
    statistics_actn: QAction = None
    svc_actn: QAction = None

    menu_user: QMenuBar = None
    login_actn: QAction = None
    registration_actn: QAction = None
    edit_users_actn: QAction = None
    profiles_group: QActionGroup = None
    profiles_submenu: QMenu = None
    logout_actn: QAction = None
