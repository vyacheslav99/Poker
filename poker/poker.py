import sys
# import argparse
from PyQt5.QtWidgets import QApplication  #, QStyleFactory

from gui import main

# список доступных стилей графического интерфейса
# ключи задаются в методе QApplication.setStyle(style)
# print(QStyleFactory.keys())


def run():
    # ap = argparse.ArgumentParser()

    # ap.add_argument('--cheats_on', action='store_true', help='Включить режим читов')
    # args = ap.parse_args()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    f = app.font()
    f.setPointSize(10)
    app.setFont(f)

    # не убирай переменную wnd!!! Без нее приложение не работает - процесс есть, а окно пропадает
    # т.е. просто main.MainWnd(app) не работает - надо обязательно присвоить его переменной
    wnd = main.MainWnd(app, *sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
