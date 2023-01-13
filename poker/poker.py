import sys, os
# import argparse
from PyQt5.QtWidgets import QApplication

from domain.models.params import Params
from gui import const
from gui import main


def run():
    # ap = argparse.ArgumentParser()

    # ap.add_argument('--cheats_on', action='store_true', help='Включить режим читов')
    # args = ap.parse_args()
    params = Params(filename=const.PARAMS_FILE if os.path.exists(const.PARAMS_FILE) else None)
    app = QApplication(sys.argv)
    app.setStyle(params.style)
    f = app.font()
    f.setPointSize(10)
    app.setFont(f)

    # не убирай переменную wnd!!! Без нее приложение не работает - процесс есть, а окно пропадает
    # т.е. просто main.MainWnd(app) не работает - надо обязательно присвоить его переменной
    wnd = main.MainWnd(app, *sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
