from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFrame, QMessageBox, QLabel, QAction
from PyQt5.QtGui import QIcon

from configs import settings


class MainWnd(QMainWindow):

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.setWindowIcon(QIcon(settings.MainIcon))
        self.setWindowTitle(settings.MainWindowTitle)
        self.init_menu_actions()

        sb_scales = (1, 2, 0)
        self.status_labels = []
        for i in range(3):
            self.status_labels.append(QLabel())
            self.statusBar().addWidget(self.status_labels[i], sb_scales[i])

        self.area = QFrame(self)
        self.area.setFocusPolicy(Qt.StrongFocus)
        self.setCentralWidget(self.area)

        self.resize(1400, 960)
        self.center()
        self.show()

    def init_menu_actions(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Файл')
        toolbar = self.addToolBar('Выход')
        # exit_acnt = QAction(QIcon('exit24.png'), 'Exit', self)
        exit_actn = QAction('Выход', self)
        exit_actn.setShortcut('Esc')
        exit_actn.setStatusTip('Выход из игры')
        exit_actn.triggered.connect(self.close)
        file_menu.addAction(exit_actn)
        toolbar.addAction(exit_actn)

        help_actn = QAction('Помощь', self)
        help_actn.setShortcut('F1')
        help_actn.setStatusTip('Помощь')
        help_actn.triggered.connect(self.show_help)
        file_menu.addAction(help_actn)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, 10)  # (screen.height() - size.height()) / 3)

    def closeEvent(self, event):
        print('< Exit >')
        super(MainWnd, self).closeEvent(event)

    def show_help(self):
        QMessageBox.information(self.parent(), 'Подсказка',
                                '\n'.join(('Клавиши управления игрой\n',) + settings.HELP_KEYS), QMessageBox.Ok)

    def set_status_messages(self, messages):
        """
        Записать сообщение в статусбар

        :param messages: list, tuple: массив сообщений. Сообщения распределяются по индексам:
            0 - в первую панель статусбара (слева - направо), 1 - во вторую и т.д.
            Длина списка сообщений не должна превышать кол-во панелей статусбара. Все, что больше, будет игнорироваться
        """

        for i in range(len(messages)):
            if i < len(self.status_labels):
                self.status_labels[i].setText(messages[i])

    def set_status_message(self, message, index=0):
        """
        Записать сообщение в статусбар

        :param message: str: Строка сообщения.
        :param index: int: Индекс панели статусбара, где надо вывести сообщение
        """

        if 0 < index < len(self.status_labels):
            self.status_labels[index].setText(message)

    def clear_status_messages(self):
        self.set_status_messages(('', '', ''))
