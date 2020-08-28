import sys
# import argparse
from PyQt5.QtWidgets import QApplication

from gui import main


def run():
    # ap = argparse.ArgumentParser()

    # ap.add_argument('--cheats_on', action='store_true', help='Включить режим читов')
    # args = ap.parse_args()

    app = QApplication(sys.argv)
    # не убирай переменную wnd!!! Без нее приложение не работает - процесс есть, а окно пропадает
    # т.е. просто main.MainWnd(app) не работает - надо обязательно присвоить его переменной
    app.setStyle('Fusion')
    wnd = main.MainWnd(app, *sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
