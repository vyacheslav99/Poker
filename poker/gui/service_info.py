from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui import const
from game import const as eng_const


class ServiceInfoDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._players = None
        self.form = None
        self.player_labels = []

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/svc.ico'))
        self.setWindowTitle('Служебная информация')
        self.setModal(False)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        # self.setFixedSize(*const.WINDOW_SIZE)
        self.resize(600, 400)

    def init_ui(self):
        self.form = QFormLayout()

        for _ in range(3):
            lb = QLabel()
            lb.setTextFormat(Qt.RichText)
            f = lb.font()
            f.setPointSize(9)
            lb.setFont(f)
            # lb.resize(*size)
            self.form.addRow(lb)
            self.player_labels.append(lb)

        self.setLayout(self.form)

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, players):
        self._players = players
        self.refresh()

    def refresh(self):
        def fmt_lear(lear):
            if lear < 2:
                c = 'black'
            else:
                c = 'red'

            return f'<span style="color: {c}">{eng_const.LEAR_SYMBOLS[lear]}</span>'

        tmpl = '<b>{0}</b>: {1}<br>{2}'
        i = 0

        for p in self.players:
            if p.is_robot:
                c = ' : '.join([f"{'Дж' if c.joker else eng_const.CARD_LETTERS[c.value]} " \
                                f"{'' if c.joker else fmt_lear(c.lear)}" for c in p.cards])
                o = ' : '.join([f"{'Дж' if c.joker else eng_const.CARD_LETTERS[c.value]} " \
                                f"{'' if c.joker else fmt_lear(c.lear)}" for c in p.order_cards])

                self.player_labels[i].setText(tmpl.format(p.name, c, o))
                i += 1
