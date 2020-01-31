from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5.QtGui import QIcon

from poker.gui.forms.main import GameArea
from poker.gui import config


class Application(QMainWindow):

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.area = GameArea(self)
        self.setCentralWidget(self.area)
        self.setWindowIcon(QIcon(config.MainIcon))
        self.setWindowTitle(config.MainWindowTitle)

        self.resize(1400, 960)
        self.center()
        self.show()
        self.area.start()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def closeEvent(self, event):
        print('< Exit >')
        super(Application, self).closeEvent(event)
