from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from gui.common import const
from gui.common.utils import handle_client_exception
from gui.common.client import GameServerClient


class SessionsDialog(QDialog):

    _columns_ = (
        ('is_current', 'This?', 'Текущий сеанс'),
        ('text', 'Информация о сеансе', ''),
        ('close_btn', '  ', '')
    )

    def __init__(self, parent, game_cvc_cli: GameServerClient):
        super().__init__(parent)

        self.game_svc_cli = game_cvc_cli
        self._sessions = []
        self._grid = None

        self.setWindowIcon(QIcon(f'{const.RES_DIR}/list.ico'))
        self.setWindowTitle('Сеансы пользователя')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        self.set_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        buttons_box = QHBoxLayout()
        buttons_box.setAlignment(Qt.AlignRight)
        ib_box = QHBoxLayout()
        ib_box.setAlignment(Qt.AlignLeft)

        btn_reset = QPushButton(' Завершить все сеансы ')
        btn_reset.setToolTip('Завершить все сеансы, кроме текущего')
        btn_reset.clicked.connect(self._close_all_sessions)
        ib_box.addWidget(btn_reset)
        buttons_box.addLayout(ib_box, 1)

        btn_close = QPushButton('Закрыть')
        btn_close.setDefault(True)
        btn_close.setFixedWidth(140)
        btn_close.clicked.connect(self.close)
        btn_close.setShortcut('Esc')
        buttons_box.addWidget(btn_close)

        # Таблица сеансов
        self._grid = QTableWidget(self)
        self._grid.setColumnCount(len(self._columns_))
        # self._grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._grid.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._grid.setSelectionMode(QAbstractItemView.NoSelection)
        self._grid.setSortingEnabled(False)
        vhead = self._grid.verticalHeader()
        vhead.setSectionResizeMode(QHeaderView.Fixed)
        vhead.setDefaultSectionSize(36)

        # шапка
        for i, value in enumerate(self._columns_):
            if i == 1:
                sz = 400
            else:
                sz = 25

            item = QTableWidgetItem(value[1])
            item.setToolTip(value[2])
            self._grid.setHorizontalHeaderItem(i, item)
            self._grid.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch if i == 1 else QHeaderView.Fixed)
            self._grid.horizontalHeader().resizeSection(i, sz)

        main_layout.addWidget(self._grid)
        main_layout.addLayout(buttons_box)
        self.setLayout(main_layout)
        btn_close.setFocus()
        self.resize(900, 300)

    def set_data(self):
        try:
            self._sessions = self.game_svc_cli.get_sessions()
        except Exception as err:
            handle_client_exception(self, err, before_msg='Не удалось загрузить данные о сеансах')
            self._sessions = []

        self._grid.setRowCount(0)
        self._grid.setRowCount(len(self._sessions))

        for row, sess in enumerate(self._sessions):
            for col, value in enumerate(self._columns_):
                if col == 0:
                    self.set_bool_item(row, col, sess.is_current)
                elif col == 1:
                    self.set_text_item(
                        row, col, sess.client_info.get('user_agent', '-= no data =-').replace('|', ' :: '),
                        bold=sess.is_current, data=sess.sid
                    )
                else:
                    self.set_button_item(row, col, sess.sid, is_current=sess.is_current)

    def set_item(self, row, col, item, bold=False):
        if col == 0:
            align = Qt.AlignLeft
        else:
            align = Qt.AlignCenter

        if bold:
            f = item.font()
            f.setBold(True)
            item.setFont(f)

        item.setTextAlignment(align | Qt.AlignVCenter)
        self._grid.setItem(row, col, item)

    def set_text_item(self, row, col, value, bold=False, data=None):
        item = QTableWidgetItem(str(value))

        if data:
            item.setData(Qt.WhatsThisRole, data)

        self.set_item(row, col, item, bold=bold)

    def set_button_item(self, row, col, value, is_current: bool = False):
        cell_widget = QWidget()
        btn = QToolButton()
        btn.setIcon(QIcon(f'{const.RES_DIR}/cancel.png'))
        btn.setToolTip('Завершить сеанс')
        btn.setEnabled(not is_current)
        setattr(btn, 'session_id', value)
        btn.clicked.connect(self._close_session)
        layout = QHBoxLayout(cell_widget)
        layout.addWidget(btn)
        layout.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        cell_widget.setLayout(layout)
        self._grid.setCellWidget(row, col, cell_widget)

    def set_bool_item(self, row, col, value):
        cell_widget = QWidget()
        chb = QCheckBox()
        chb.setCheckState(Qt.Checked if value else Qt.Unchecked)
        chb.setEnabled(False)
        layout = QHBoxLayout(cell_widget)
        layout.addWidget(chb)
        layout.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        cell_widget.setLayout(layout)
        self._grid.setCellWidget(row, col, cell_widget)

    def _close_session(self):
        button = self.sender()
        session_id = button.session_id

        res = QMessageBox.question(
            self, 'Подтверждение', f'Завершить выбранный сеанс ({session_id})?',
            QMessageBox.Yes | QMessageBox.No
        )

        if res == QMessageBox.No:
            return

        try:
            self.game_svc_cli.close_session(session_id)
            self.set_data()
        except Exception as err:
            handle_client_exception(self, err, before_msg='Не удалось завершить сеанс')

    def _close_all_sessions(self):
        res = QMessageBox.question(
            self, 'Подтверждение', 'Завершить все сеансы, кроме текущего?', QMessageBox.Yes | QMessageBox.No
        )

        if res == QMessageBox.No:
            return

        try:
            res = self.game_svc_cli.close_another_sessions()
            QMessageBox.information(self, 'Готово', f'Завершено сеансов: {res}')
            self.set_data()
        except Exception as err:
            handle_client_exception(self, err, before_msg='Не удалось все сеансы')
