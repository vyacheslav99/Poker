import os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from models.params import Profiles
from gui.common import const
from gui.common.client import GameServerClient
from gui.common.graphics import Face2


class ProfilesNetDialog(QDialog):

    def __init__(self, parent, profiles: Profiles, curr_profile):
        super().__init__(parent)

        self.game_svc_cli: GameServerClient = parent.game_server_cli
        self._profiles = profiles

        # элементы управления
        self._selected_profile = None
        self._uid_edit = None
        self._username = None
        self._login = None
        self._curr_password = None
        self._new_password = None
        self._confirm_password = None
        self._avatar = None
        self._avatar_btn = None
        self._save_btn = None
        self._info_lb = None

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/profile.ico'))
        self.setWindowTitle('Профили пользователей')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self._selected_profile.setCurrentIndex(self._profiles.get_item(curr_profile)[0])
        self._on_profile_change()

    def init_ui(self):
        # Кнопка Закрыть
        main_layout = QVBoxLayout()
        btn_close = QPushButton('Закрыть')
        btn_close.setDefault(True)
        btn_close.setFixedWidth(140)
        btn_close.clicked.connect(self.accept)
        buttons_box = QHBoxLayout()
        buttons_box.setAlignment(Qt.AlignRight)
        buttons_box.addWidget(btn_close)

        # Выбор профиля
        l2 = QHBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Профиль'))
        l2.addSpacing(70)
        self._selected_profile = QComboBox()
        self._selected_profile.setEditable(False)
        self._selected_profile.setFixedWidth(290)

        for p in self._profiles.profiles:
            self._selected_profile.addItem(p.name, QVariant(p.uid))

        self._selected_profile.currentIndexChanged.connect(self._on_profile_change)
        l2.addWidget(self._selected_profile)
        main_layout.addLayout(l2)

        # Настройки выбранного профиля
        group = QGroupBox()
        layout = QGridLayout()
        layout.setHorizontalSpacing(20)
        row = 0

        # uid профиля
        row += 1
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('uid профиля'))
        l2.addSpacing(10)
        self._uid_edit = QLineEdit()
        self._uid_edit.setReadOnly(True)
        self._uid_edit.setFixedWidth(290)
        self._uid_edit.setPlaceholderText('< пользователь не выбран >')
        l2.addWidget(self._uid_edit)
        layout.addLayout(l2, row, 1, Qt.AlignLeft | Qt.AlignTop)

        # Имя игрока
        row += 1
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Имя игрока'))
        l2.addSpacing(10)
        self._username = QLineEdit()
        self._username.setFixedWidth(290)
        self._username.textEdited.connect(self._validate)
        l2.addWidget(self._username)
        layout.addLayout(l2, row, 1, Qt.AlignLeft)

        # Логин
        row += 1
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Логин'))
        l2.addSpacing(10)
        self._login = QLineEdit()
        self._login.setFixedWidth(290)
        self._login.textEdited.connect(self._validate)
        l2.addWidget(self._login)
        layout.addLayout(l2, row, 1, Qt.AlignLeft)

        # Изменение пароля
        row += 1
        layout.addWidget(QLabel('<b>Смена пароля</b>'), row, 1, Qt.AlignLeft)
        line = QFrame()
        line.setFixedWidth(290)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, row, 1, Qt.AlignHCenter | Qt.AlignRight)

        # Текущий пароль
        row += 1
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Текущий пароль'))
        l2.addSpacing(20)
        self._curr_password = QLineEdit()
        self._curr_password.setFixedWidth(290)
        self._curr_password.setEchoMode(QLineEdit.Password)
        self._curr_password.textEdited.connect(self._validate)
        l2.addWidget(self._curr_password)
        layout.addLayout(l2, row, 1, Qt.AlignLeft)

        # Новый пароль
        row += 1
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Новый пароль'))
        l2.addSpacing(10)
        self._new_password = QLineEdit()
        self._new_password.setFixedWidth(290)
        self._new_password.setEchoMode(QLineEdit.Password)
        self._new_password.textEdited.connect(self._validate)
        l2.addWidget(self._new_password)
        layout.addLayout(l2, row, 1, Qt.AlignLeft)

        # Повтор пароля
        row += 1
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Повтор пароля'))
        l2.addSpacing(10)
        self._confirm_password = QLineEdit()
        self._confirm_password.setFixedWidth(290)
        self._confirm_password.setEchoMode(QLineEdit.Password)
        self._confirm_password.textEdited.connect(self._validate)
        l2.addWidget(self._confirm_password)
        layout.addLayout(l2, row, 1, Qt.AlignLeft)

        row += 1
        self._info_lb = QLabel()
        layout.addWidget(self._info_lb, row, 1, Qt.AlignLeft)

        # кнопка Сохранить
        row += 1
        self._save_btn = QPushButton(QIcon(f'{const.RES_DIR}/save.ico'), '  Сохранить')
        self._save_btn.setFixedWidth(140)
        self._save_btn.setToolTip('Сохранить изменения в профиле')
        self._save_btn.clicked.connect(self._save_profile)
        layout.addWidget(self._save_btn, row, 1, Qt.AlignBottom)

        # аватарка
        menu = QMenu()
        sel_av = QAction(QIcon(f'{const.RES_DIR}/edit.ico'), 'Изменить', self)
        sel_av.triggered.connect(self._select_avatar)
        menu.addAction(sel_av)
        clear_av = QAction(QIcon(f'{const.RES_DIR}/cancel.png'), 'Очистить', self)
        clear_av.triggered.connect(self._clear_avatar)
        menu.addAction(clear_av)
        l2 = QVBoxLayout()
        self._avatar_btn = QToolButton()
        self._avatar_btn.setFixedSize(QSize(190, 190))
        self._avatar_btn.setToolTip('Нажми, чтобы изменить аватарку')
        self._avatar_btn.setIconSize(QSize(*const.USER_FACE_SIZE))
        self._avatar_btn.setIcon(QIcon(QPixmap(f'{const.FACE_DIR}/noImage.png')))
        self._avatar_btn.setPopupMode(QToolButton.InstantPopup)
        self._avatar_btn.setMenu(menu)
        self._avatar = QLabel()
        l2.addWidget(self._avatar_btn)
        layout.addLayout(l2, 1, 2, row, 1, Qt.AlignTop)

        group.setLayout(layout)
        main_layout.addWidget(group)
        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)

    def _on_profile_change(self):
        p = self._profiles.get(self._selected_profile.currentData())
        self._info_lb.setText('')

        if p:
            self._uid_edit.setText(p.uid)
            self._username.setText(p.name)
            self._login.setText(p.login)
            self._curr_password.setText('')
            self._new_password.setText('')
            self._confirm_password.setText('')
            self._avatar.setText(p.avatar)
            self._avatar_btn.setIcon(QIcon(Face2(p)))
        else:
            self._clear()

    def _validate(self):
        is_valid = False
        errs = []
        curr_player = self._profiles.get(self._selected_profile.currentData())

        if not self._username.text():
            errs.append('Имя пользователя пустое')

        login = self._login.text()

        if not login:
            errs.append('Логин пустой')
        elif not set(login).issubset(set(const.LOGIN_ALLOW_LITERALS)):
            errs.append('Логин содержит недопустимые символы')
        elif len(login) < 3:
            errs.append('Логин слишком короткий')
        else:
            try:
                if curr_player.login != login:
                    is_free = self.game_svc_cli.username_is_free(login)
                    if not is_free:
                        errs.append('Такой логин уже существует')
            except Exception:
                pass

        curr_passwd = self._curr_password.text()
        new_passwd = self._new_password.text()
        confirm_passwd = self._confirm_password.text()

        if new_passwd:
            if not curr_passwd:
                errs.append('Текущий пароль пустой')
            if not set(curr_passwd).issubset(set(const.PASSWORD_ALLOW_LITERALS)):
                errs.append('Текущий пароль содержит недопустимые символы')
            if not set(new_passwd).issubset(set(const.PASSWORD_ALLOW_LITERALS)):
                errs.append('Новый пароль содержит недопустимые символы')

            if new_passwd != confirm_passwd:
                errs.append('Пароль и повтор пароля не совпадают')

        if errs:
            self._save_btn.setToolTip('<br>'.join(errs))
            self._info_lb.setStyleSheet('QLabel {color: maroon}')
        else:
            is_valid = True
            self._save_btn.setToolTip('')

        self._info_lb.setText(self._save_btn.toolTip())
        self._save_btn.setEnabled(is_valid)
        return is_valid

    def _clear(self):
        self._uid_edit.setText('')
        self._username.setText('')
        self._login.setText('')
        self._curr_password.setText('')
        self._new_password.setText('')
        self._confirm_password.setText('')
        self._avatar.setText('')
        self._avatar_btn.setIcon(QIcon(QPixmap(f'{const.FACE_DIR}/noImage.png')))

    def _save_profile(self):
        # todo: Пока ничего не сохраняем
        return

        if not self._validate():
            return

        uid = self._selected_profile.currentData()
        avatar = self._avatar.text()
        user = self._profiles.get(uid)
        self._selected_profile.setItemText(self._selected_profile.currentIndex(), self._username.text())

        user.login = self._login.text()
        user.password = self._new_password.text()
        user.name = self._username.text()
        user.avatar = os.path.split(avatar)[1] if avatar else None

        self._profiles.set_profile(user)

        if avatar:
            fldr = f'{const.PROFILES_DIR}/{uid}'
            if not os.path.isdir(fldr):
                os.makedirs(fldr)

            pixmap = self._load_image(avatar)
            pixmap.save(os.path.join(fldr, user.avatar), None, -1)

        self._info_lb.setStyleSheet('QLabel {color: navy}')
        self._info_lb.setText('Изменения сохранены')

    def _select_avatar(self):
        filename = QFileDialog.getOpenFileName(
            self, 'Выбери картинку', '', 'Изображения (*.bmp *.jpg *.jpeg *.png *.ico)'
        )[0]

        if filename:
            self._avatar.setText(filename)
            self._avatar_btn.setIcon(QIcon(self._load_image(filename)))

    def _clear_avatar(self):
        self._avatar.setText('')
        self._avatar_btn.setIcon(QIcon(QPixmap(f'{const.FACE_DIR}/noImage.png')))

    def _load_image(self, filename) -> QPixmap:
        pixmap = QPixmap(filename)
        sz = pixmap.size()

        if sz.width() != const.USER_FACE_SIZE[0] or sz.height() != const.USER_FACE_SIZE[1]:
            x, y = 0, 0

            if sz.width() > sz.height():
                mode = Qt.KeepAspectRatio
            elif sz.width() < sz.height():
                mode = Qt.KeepAspectRatioByExpanding
                y = 10
            else:
                mode = Qt.IgnoreAspectRatio

            pixmap = pixmap.scaled(QSize(*const.USER_FACE_SIZE), mode, Qt.SmoothTransformation)
            pixmap = pixmap.copy(x, y, const.USER_FACE_SIZE[0], const.USER_FACE_SIZE[1])

        return pixmap
