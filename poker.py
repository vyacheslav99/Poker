import sys
import os
# import argparse
import logging

from PyQt5.QtWidgets import QApplication

from gui import config
from gui.common import const
from gui.main_single import SinglePlayerMainWnd
from gui.main_multi import MultiPlayerMainWnd


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error('Uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))


def run():
    if not os.path.isdir(const.APP_DATA_DIR):
        os.makedirs(const.APP_DATA_DIR, exist_ok=True)

    logging.basicConfig(**config.logging_config())
    sys.excepthook = handle_exception

    logging.info('-' * 120)
    logging.info('-= Start poker application =-')
    logging.debug('Enabled DEDUG mode logging level!')

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
