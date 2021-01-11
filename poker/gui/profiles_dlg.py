from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const
from gui.graphics import Face2
from modules.core import const as eng_const
from modules.params import Profiles


class ProfilesDialog(QDialog):

    def __init__(self, parent, profiles: Profiles, curr_profile):
        super().__init__(parent)
        self._profiles = profiles

        # элементы управления
        self._select_profile = None
        self._uid_edit = None
        self._username = None
        self._login = None
        self._password = None
        self._avatar = None
        self._avatar_btn = None
        self._save_btn = None

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/player.ico'))
        self.setWindowTitle('Профили пользователей')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self._select_profile.setCurrentIndex(self._profiles.get_item(curr_profile)[0])
        self._on_profile_change()

    def init_ui(self):
        # Кнопки ОК, Отмена
        main_layout = QVBoxLayout()
        btn_close = QPushButton('Закрыть')
        # btn_close.setDefault(True)
        btn_close.setFixedWidth(140)
        btn_close.clicked.connect(self.reject)
        buttons_box = QHBoxLayout()
        buttons_box.setAlignment(Qt.AlignRight)
        buttons_box.addWidget(btn_close)

        # Выбор профиля
        l2 = QHBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Профиль'))
        l2.addSpacing(45)
        self._select_profile = QComboBox()
        self._select_profile.setEditable(False)
        self._select_profile.setFixedWidth(205)

        for p in self._profiles.profiles:
            self._select_profile.addItem(p.name, QVariant(p.uid))

        self._select_profile.currentIndexChanged.connect(self._on_profile_change)
        l2.addWidget(self._select_profile)

        # Кнопка добавления профиля
        btn_add = QPushButton(QIcon(f'{const.RES_DIR}/plus.ico'), '')
        btn_add.setFixedWidth(35)
        btn_add.setToolTip('Добавить новый профиль')
        btn_add.clicked.connect(self._add_profile)
        l2.addWidget(btn_add)

        # Кнопка удаления профиля
        btn_del = QPushButton(QIcon(f'{const.RES_DIR}/minus.ico'), '')
        btn_del.setFixedWidth(35)
        btn_del.setToolTip('Удалить выбранный профиль')
        btn_del.clicked.connect(self._del_profile)
        l2.addWidget(btn_del)

        main_layout.addLayout(l2)

        # Настройки выбранного профиля
        group = QGroupBox()
        layout = QGridLayout()
        layout.setHorizontalSpacing(20)

        # uid профиля
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('uid профиля'))
        l2.addSpacing(10)
        self._uid_edit = QLineEdit()
        self._uid_edit.setReadOnly(True)
        self._uid_edit.setFixedWidth(290)
        self._uid_edit.setPlaceholderText('< пользователь не выбран >')
        l2.addWidget(self._uid_edit)
        layout.addLayout(l2, 1, 1, Qt.AlignLeft)

        # Имя игрока
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Имя игрока'))
        l2.addSpacing(20)
        self._username = QLineEdit()
        self._username.setFixedWidth(290)
        l2.addWidget(self._username)
        layout.addLayout(l2, 2, 1, Qt.AlignLeft)

        # Логин
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Логин'))
        l2.addSpacing(30)
        self._login = QLineEdit()
        self._login.setFixedWidth(290)
        l2.addWidget(self._login)
        layout.addLayout(l2, 3, 1, Qt.AlignLeft)

        # Пароль
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Пароль'))
        l2.addSpacing(30)
        self._password = QLineEdit()
        self._password.setFixedWidth(290)
        self._password.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        # self._password.setEnabled(False)
        l2.addWidget(self._password)
        layout.addLayout(l2, 4, 1, Qt.AlignLeft)

        # кнопка Сохранить
        self._save_btn = QPushButton()
        self._avatar_btn.setFixedSize(QSize(190, 190))
        self._avatar_btn.setToolTip('Нажми, чтобы выбрать аватарку')
        self._avatar_btn.setIconSize(QSize(180, 180))
        self._avatar_btn.setIcon(QIcon(QPixmap(f'{const.FACE_DIR}/noImage.png')))
        self._avatar_btn.clicked.connect(self._select_avatar)
        self._avatar = QLabel()
        l2.addWidget(self._avatar_btn)
        # l2.addSpacing(5)
        # l2.addWidget(self._avatar)
        layout.addLayout(l2, 1, 2, 5, 1, Qt.AlignBaseline)

        # аватарка
        l2 = QVBoxLayout()
        self._avatar_btn = QPushButton()
        self._avatar_btn.setFixedSize(QSize(190, 190))
        self._avatar_btn.setToolTip('Нажми, чтобы выбрать аватарку')
        self._avatar_btn.setIconSize(QSize(180, 180))
        self._avatar_btn.setIcon(QIcon(QPixmap(f'{const.FACE_DIR}/noImage.png')))
        self._avatar_btn.clicked.connect(self._select_avatar)
        self._avatar = QLabel()
        l2.addWidget(self._avatar_btn)
        # l2.addSpacing(5)
        # l2.addWidget(self._avatar)
        layout.addLayout(l2, 1, 2, 5, 1, Qt.AlignBaseline)

        group.setLayout(layout)
        main_layout.addWidget(group)
        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)

    def _on_profile_change(self):
        p = self._profiles.get(self._select_profile.currentData())

        if p:
            self._uid_edit.setText(p.uid)
            self._username.setText(p.name)
            self._login.setText(p.login)
            self._password.setText(p.password)
            self._avatar.setText(p.avatar)
            self._avatar_btn.setIcon(QIcon(Face2(p)))
        else:
            self._uid_edit.setText('')
            self._username.setText('')
            self._login.setText('')
            self._password.setText('')
            self._avatar.setText('')
            self._avatar_btn.setIcon(QIcon(QPixmap(f'{const.FACE_DIR}/noImage.png')))

    def _add_profile(self):
        p = self._profiles.create()
        self._select_profile.addItem(p.name, QVariant(p.uid))
        self._select_profile.setCurrentIndex(self._profiles.get_item(p.uid)[0])

    def _del_profile(self):
        pass

    def _select_avatar(self):
        pass
