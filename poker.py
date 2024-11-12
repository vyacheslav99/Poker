import sys
# import argparse
from PyQt5.QtWidgets import QApplication
from gui.main_single import SinglePlayerMainWnd
from gui.main_multi import MultiPlayerMainWnd


def run():
    # ap = argparse.ArgumentParser()

    # ap.add_argument('--cheats_on', action='store_true', help='Включить режим читов')
    # args = ap.parse_args()
    app = QApplication(sys.argv)

    # не убирай переменную wnd!!! Без нее приложение не работает - процесс есть, а окно пропадает
    # т.е. просто main.MainWnd(app) не работает - надо обязательно присвоить его переменной

    if '--mp' in sys.argv:
        cls = MultiPlayerMainWnd
    else:
        cls = SinglePlayerMainWnd

    wnd = cls(app, *sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
