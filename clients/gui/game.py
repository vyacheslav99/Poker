import sys
# import argparse
from PyQt5.QtWidgets import QApplication

import app


def run():
    # ap = argparse.ArgumentParser()

    # ap.add_argument('--cheats_on', action='store_true', help='Включить режим читов')
    # args = ap.parse_args()

    qapp = QApplication(sys.argv)
    poker = app.Application(qapp)
    sys.exit(qapp.exec_())


if __name__ == '__main__':
    run()
