import os
import shutil
import string

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const
from gui.graphics import Face2
from models.params import Profiles


class ProfilesDialog(QDialog):

    def __init__(self, parent, profiles: Profiles, curr_profile):
        super().__init__(parent)
        self._profiles = profiles
        self._curr_profile = curr_profile
        self._curr_changed = False

        # элементы управления
        self._selected_profile = None
        self._uid_edit = None
        self._username = None
        self._login = None
        # self._password = None
        self._avatar = None
        self._avatar_btn = None
        self._save_btn = None
        self._info_lb = None

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/player.ico'))
        self.setWindowTitle('Профили пользователей')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self._selected_profile.setCurrentIndex(self._profiles.get_item(curr_profile)[0])
        self._on_profile_change()

    def close(self) -> bool:
        if self._curr_changed:
            self.accept()
        else:
            self.reject()
        
        super(ProfilesDialog, self).close()

    def init_ui(self):
        # Кнопка Закрыть
        main_layout = QVBoxLayout()
        btn_close = QPushButton('Закрыть')
        btn_close.setDefault(True)
        btn_close.setFixedWidth(140)
        btn_close.clicked.connect(self.close)
        buttons_box = QHBoxLayout()
        buttons_box.setAlignment(Qt.AlignRight)
        buttons_box.addWidget(btn_close)

        # Выбор профиля
        l2 = QHBoxLayout()
        l2.setAlignment(Qt.AlignLeft)
        l2.addWidget(QLabel('Профиль'))
        l2.addSpacing(45)
        self._selected_profile = QComboBox()
        self._selected_profile.setEditable(False)
        self._selected_profile.setFixedWidth(205)

        for p in self._profiles.profiles:
            self._selected_profile.addItem(p.name, QVariant(p.uid))

        self._selected_profile.currentIndexChanged.connect(self._on_profile_change)
        l2.addWidget(self._selected_profile)

        # Кнопка добавления профиля
        btn_add = QToolButton()
        btn_add.setIcon(QIcon(f'{const.RES_DIR}/plus.ico'))
        btn_add.setFixedWidth(35)
        btn_add.setToolTip('Добавить новый профиль')
        btn_add.clicked.connect(self._add_profile)
        l2.addWidget(btn_add)

        # Кнопка удаления профиля
        btn_del = QToolButton()
        btn_del.setIcon(QIcon(f'{const.RES_DIR}/minus.ico'))
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
        self._username.editingFinished.connect(self._name_edited)
        l2.addWidget(self._username)
        layout.addLayout(l2, 2, 1, Qt.AlignLeft)

        # Логин
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Логин'))
        l2.addSpacing(30)
        self._login = QLineEdit()
        self._login.setFixedWidth(290)
        self._login.editingFinished.connect(self._validate)
        l2.addWidget(self._login)
        layout.addLayout(l2, 3, 1, Qt.AlignLeft)

        # Пароль
        # l2 = QHBoxLayout()
        # l2.addWidget(QLabel('Пароль'))
        # l2.addSpacing(30)
        # self._password = QLineEdit()
        # self._password.setFixedWidth(290)
        # self._password.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        # # self._password.setEnabled(False)
        # self._password.editingFinished.connect(self._validate)
        # l2.addWidget(self._password)
        # layout.addLayout(l2, 4, 1, Qt.AlignLeft)

        # кнопка Сохранить
        self._info_lb = QLabel()
        layout.addWidget(self._info_lb, 4, 1, Qt.AlignBottom)
        self._save_btn = QPushButton(QIcon(f'{const.RES_DIR}/save.ico'), '  Сохранить')
        self._save_btn.setFixedWidth(140)
        self._save_btn.setToolTip('Сохранить изменения в профиле')
        self._save_btn.clicked.connect(self._save_profile)
        layout.addWidget(self._save_btn, 5, 1, Qt.AlignBottom)

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
        # self._avatar_btn.clicked.connect(self._select_avatar)
        self._avatar_btn.setMenu(menu)
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
        p = self._profiles.get(self._selected_profile.currentData())
        self._info_lb.setText('')

        if p:
            self._uid_edit.setText(p.uid)
            self._username.setText(p.name)
            self._login.setText(p.login)
            # self._password.setText(p.password)
            self._avatar.setText(p.avatar)
            self._avatar_btn.setIcon(QIcon(Face2(p)))
        else:
            self._clear()

    def _name_edited(self):
        self._selected_profile.setItemText(self._selected_profile.currentIndex(), self._username.text())
        self._validate()

    def _validate(self):
        is_valid = False
        errs = []

        if not self._username.text():
            errs.append('Имя пользователя пустое')

        s = self._login.text()
        if not s:
            errs.append('Логин пустой')
        elif not set(s).issubset(set(string.printable)):
            errs.append('Логин содержит неверные символы. Вводи логин в английской раскладке')
        elif [x for x in self._profiles.filter('login', s) if x.uid != self._uid_edit.text()]:
            errs.append('Такой логин уже существует. Придумай другой')

        # s = self._password.text()
        # if s and not set(s).issubset(set(string.printable)):
        #     errs.append('Пароль содержит неверные символы. Вводи пароль в английской раскладке')

        if errs:
            self._save_btn.setToolTip('<br>'.join(errs))
            self._info_lb.setStyleSheet('QLabel {color: maroon}')
            self._info_lb.setText(self._save_btn.toolTip())
        else:
            is_valid = True
            self._save_btn.setToolTip('')

        self._save_btn.setEnabled(is_valid)
        return is_valid

    def _clear(self):
        self._uid_edit.setText('')
        self._username.setText('')
        self._login.setText('')
        # self._password.setText('')
        self._avatar.setText('')
        self._avatar_btn.setIcon(QIcon(QPixmap(f'{const.FACE_DIR}/noImage.png')))

    def _add_profile(self):
        user = self._profiles.generate()
        self._selected_profile.addItem(user.name, QVariant(user.uid))
        self._selected_profile.setCurrentIndex(self._selected_profile.count() - 1)
        self._uid_edit.setText(user.uid)
        self._username.setText(user.name)
        self._login.setText(user.login)
        # self._password.setText(user.password)
        self._avatar.setText(user.avatar)
        self._avatar_btn.setIcon(QIcon(Face2(user)))

    def _del_profile(self):
        i = self._selected_profile.currentIndex()
        uid = self._selected_profile.currentData()

        if uid == self._curr_profile:
            QMessageBox.warning(self, 'Ошибка', 'Невозможно удалить текущий профиль!\nСначала смените текущий профиль '
                                                'в настройках программы.')
            return

        res = QMessageBox.question(self, 'Подтверждение',
                                   f'Хотите удалить этот профиль?\nЭто действие будет невозможно отменить!',
                                   QMessageBox.Yes | QMessageBox.No)

        if res == QMessageBox.No:
            return

        self._profiles.delete(uid)
        self._selected_profile.removeItem(i)

        fldr = f'{const.PROFILES_DIR}/{uid}'
        if os.path.isdir(fldr):
            shutil.rmtree(fldr)

    def _save_profile(self):
        if not self._validate():
            return

        uid = self._selected_profile.currentData()
        user = self._profiles.get(self._selected_profile.currentData())
        avatar = self._avatar.text()

        if not user:
            user = self._profiles.generate(**{
                'uid': uid,
                'login': self._login.text(),
                # 'password': self._password.text(),
                'name': self._username.text(),
                'avatar': os.path.split(avatar)[1]
            })
        else:
            user.login = self._login.text()
            # user.password = self._password.text()
            user.name = self._username.text()
            user.avatar = os.path.split(avatar)[1]

        self._profiles.set_profile(user)

        if uid == self._curr_profile:
            self._curr_changed = True

        if avatar:
            fldr = f'{const.PROFILES_DIR}/{uid}'
            if not os.path.isdir(fldr):
                os.makedirs(fldr)

            pixmap = self._load_image(avatar)
            pixmap.save(os.path.join(fldr, user.avatar), None, -1)

        self._info_lb.setStyleSheet('QLabel {color: navy}')
        self._info_lb.setText('Изменения сохранены')

    def _select_avatar(self):
        filename = QFileDialog.getOpenFileName(self, 'Выбери картинку', '', 'Изображения (*.bmp *.jpg *.jpeg *.png *.ico)')[0]

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
