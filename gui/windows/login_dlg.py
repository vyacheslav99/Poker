from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui.common import const


class LoginDialog(QDialog):

    def __init__(self, parent, login: str = None):
        super().__init__(parent)

        self._login: QLineEdit | None = None
        self._password: QLineEdit | None = None
        self._btn_ok: QPushButton | None = None
        self._info_lb: QLabel | None = None

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/login.png'))
        self.setWindowTitle('Авторизация')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

        if login:
            self._login.setText(login)

    def init_ui(self):
        self._btn_ok = QPushButton(QIcon(f'{const.RES_DIR}/ok.png'), 'OK')
        self._btn_ok.setDefault(True)
        self._btn_ok.setFixedWidth(140)
        self._btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton(QIcon(f'{const.RES_DIR}/cancel.png'), 'Отмена')
        btn_cancel.setFixedWidth(140)
        btn_cancel.clicked.connect(self.reject)
        buttons_box = QHBoxLayout()
        buttons_box.setAlignment(Qt.AlignRight)
        buttons_box.addWidget(self._btn_ok)
        buttons_box.addWidget(btn_cancel)

        layout = QGridLayout()
        layout.setHorizontalSpacing(20)

        # Логин
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Логин'))
        l2.addSpacing(30)
        self._login = QLineEdit()
        self._login.setFixedWidth(290)
        self._login.textEdited.connect(self._validate)
        l2.addWidget(self._login)
        layout.addLayout(l2, 3, 1, Qt.AlignLeft)

        # Пароль
        l2 = QHBoxLayout()
        l2.addWidget(QLabel('Пароль'))
        l2.addSpacing(30)
        self._password = QLineEdit()
        self._password.setFixedWidth(290)
        self._password.setEchoMode(QLineEdit.Password)
        self._password.textEdited.connect(self._validate)
        l2.addWidget(self._password)
        layout.addLayout(l2, 4, 1, Qt.AlignLeft)

        self._info_lb = QLabel()
        layout.addWidget(self._info_lb, 5, 1, Qt.AlignBottom | Qt.AlignRight)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)

        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)
        self._validate()
        self._btn_ok.setToolTip('')
        self._info_lb.setText(self._btn_ok.toolTip())

    def _validate(self):
        is_valid = False
        errs = []

        login = self._login.text()

        if not login:
            errs.append('Логин пустой')
        elif not set(login).issubset(set(const.LOGIN_ALLOW_LITERALS)):
            errs.append('Логин содержит недопустимые символы')

        passwd = self._password.text()

        if not passwd:
            errs.append('Пароль пустой')
        elif not set(passwd).issubset(set(const.PASSWORD_ALLOW_LITERALS)):
            errs.append('Пароль содержит недопустимые символы')

        if errs:
            self._btn_ok.setToolTip('<br>'.join(errs))
            self._info_lb.setStyleSheet('QLabel {color: maroon}')
        else:
            is_valid = True
            self._btn_ok.setToolTip('')

        self._info_lb.setText(self._btn_ok.toolTip())
        self._btn_ok.setEnabled(is_valid)

        return is_valid

    def get_login(self) -> str:
        return self._login.text().strip()

    def get_password(self) -> str:
        return self._password.text().strip()
