from PyQt5.QtWidgets import QFrame, QMessageBox, QLabel
from PyQt5.QtCore import Qt

from clients.gui import config


class GameArea(QFrame):

    def __init__(self, parent):
        super().__init__(parent)

        sb_scales = (1, 2, 0)
        self.statusbar = self.parent().statusBar()
        self.status_labels = []
        for i in range(3):
            self.status_labels.append(QLabel())
            self.statusbar.addWidget(self.status_labels[i], sb_scales[i])

        # self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

    def start(self):
        self.clear_status_messages()
        # self.timer.start(self.speed, self)
        print('< Started >')
        self.update()

    def stop(self):
        # self.timer.stop()
        print('< Stopped >')
        self.update()

    def show_help(self):
        QMessageBox.information(self.parent(), 'Подсказка',
                                '\n'.join(('Клавиши управления игрой\n',) + config.HELP_KEYS), QMessageBox.Ok)

    def print_debug_info(self):
        print('-= Window =-')
        print(f'Top: {self.parent().geometry().top()}')
        print(f'Left: {self.parent().geometry().left()}')
        print(f'Height: {self.parent().geometry().height()}')
        print(f'Width: {self.parent().geometry().width()}')
        print(f'Area Height: {self.contentsRect().height()}')
        print(f'Area Width: {self.contentsRect().width()}')

    def keyPressEvent(self, event):
        key = event.key()

        try:
            if key == Qt.Key_Escape:
                # self.parent().app.quit()
                self.parent().close()
            if key == Qt.Key_S:
                self.start()
            elif key == Qt.Key_I:
                self.print_debug_info()
            elif key == Qt.Key_F1:
                self.show_help()
            else:
                super(GameArea, self).keyPressEvent(event)
        finally:
            pass # self.update_ui()

    def timerEvent(self, event):
        try:
            super(GameArea, self).timerEvent(event)
        finally:
            pass # self.update_ui()

    def paintEvent(self, event):
        """
        for i in range(config.BoxHeight):
            for j in range(config.BoxWidth):
                self.draw_square(j, i, self.engine.cell(i, j))
        """

    # def update_ui(self):
    #     if self.isStarted and not self.isPaused:
    #         self.set_status_message(f'Размер: {self.engine.length()}')
    #     self.update()

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

        if index < len(self.status_labels):
            self.status_labels[index].setText(message)

    def clear_status_messages(self):
        self.set_status_messages(('', '', ''))
