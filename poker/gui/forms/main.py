import os, sys
import random
import json
import pickle
import datetime
from colour import Color

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFrame, QMessageBox, QLabel
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QIcon

from poker.core import engine, helpers, const


class GameArea(QFrame):

    def __init__(self, parent):
        super().__init__(parent)

        sb_scales = (1, 2, 0)
        self.statusbar = self.parent().statusBar()
        self.status_labels = []
        for i in range(3):
            self.status_labels.append(QLabel())
            self.statusbar.addWidget(self.status_labels[i], sb_scales[i])

        # self.engine = engine.Engine(config.BoxWidth, config.BoxHeight, boa_size=length, arrange_mech=arrange_mech)
        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

    def start(self):
        """
        self.spark_timer.stop()

        if self.isStarted:
            self.stop('Игра остановлена')

        self.clear_status_messages()
        self.engine.clear()
        self.sp_alg = random.choice((config.SP_ALG_RANDOM, config.SP_ALG_ALONG_BODY))
        self.body_gradient = list(Color(config.Colors[config.FIELD_TYPE_BODY][0]).range_to(
            Color(config.Colors[config.FIELD_TYPE_BODY][1]), (config.BoxWidth * config.BoxHeight) - 1))

        self.set_status_message(f'Размер: {self.engine.length()}')
        self.set_difficulty(self._next_diff)
        self.isPaused = False
        self.isStarted = True
        self.speed = self._difficulty['InitialSpeed']
        self.engine.start()
        self.timer.start(self.speed, self)
        self.acc_timer.start(config.AccInterval, self)
        self.start_time = datetime.datetime.now()
        print('< Started >')
        self.update()
        """

    def stop(self, message=''):
        """
        if not self.isStarted:
            return

        self.timer.stop()
        self.acc_timer.stop()
        self.isStarted = False
        self.isPaused = False
        self.set_status_messages((f'Размер: {self.engine.length()}', f'{message}'))
        print('< Stopped >')
        self.update()
        """

    def show_help(self):
        """
        if self.isStarted:
            self.pause()

        QMessageBox.information(self.parent(), 'Подсказка',
                                '\n'.join(('Клавиши управления игрой\n',) + config.HELP_KEYS +
                                          ('--------------------\n',) + config.HELP_CHEAT_KEYS), QMessageBox.Ok)
        """

    def print_debug_info(self):
        print('-= Window =-')
        print(f'Top: {self.parent().geometry().top()}')
        print(f'Left: {self.parent().geometry().left()}')
        print(f'Height: {self.parent().geometry().height()}')
        print(f'Width: {self.parent().geometry().width()}')
        print(f'Area Height: {self.contentsRect().height()}')
        print(f'Area Width: {self.contentsRect().width()}')

        print('')
        # self.engine.print_debug_info()

        print('')
        print('-= Game =-')
        # print(f'Cheats mode: {"ON" if self.cheats_on else "OFF"}')
        # print(f'Difficulty: {self._difficulty["EngName"]}')
        print(f'Started: {self.isStarted}')
        print(f'Paused: {self.isPaused}')

        # if self.isStarted:
        #     print(f'Start time: {self.start_time}')
        #     print(f'Total left time: {datetime.datetime.now() - self.start_time}')

    # def scale_width(self):
    #     """ масштабирование - рассчитывает размер стороны квадрата в пикселях по оси X (ширина) """
    #     return self.contentsRect().width() // config.BoxWidth

    def keyPressEvent(self, event):
        """
        key = event.key()

        try:
            if key == Qt.Key_Escape:
                # self.parent().app.quit()
                self.parent().close()
            if key == Qt.Key_S:
                self.start()
            elif key == Qt.Key_I:
                self.print_debug_info()
            elif key in (Qt.Key_P, Qt.Key_Space):
                self.pause()
            elif key in (Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5):
                self.set_difficulty((Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5).index(key) + 1)
            elif key == Qt.Key_F1:
                self.show_help()
            elif not self.isStarted or self.isPaused:
                return
            elif key == Qt.Key_F5:
                self.save(config.QuicksaveFile)
            elif key == Qt.Key_F9:
                self.load_and_start(config.QuicksaveFile)
            elif key == Qt.Key_E:
                self.stop('Игра остановлена игроком')
            elif key == Qt.Key_Right:
                self.engine.turn_right()
            elif key == Qt.Key_Left:
                self.engine.turn_left()
            elif key == Qt.Key_Up:
                self.engine.turn_up()
            elif key == Qt.Key_Down:
                self.engine.turn_down()
            # остальное только с включеным режимом читерства
            elif not self.cheats_on:
                return
            elif key == Qt.Key_B:
                self.engine.create_barriers()
            elif key == Qt.Key_C:
                self.engine.remove_barriers()
            elif key == Qt.Key_Plus:
                self.accelerate()
            elif key == Qt.Key_Minus:
                self.decelerate()
            else:
                super(GameBox, self).keyPressEvent(event)
        except engine.StopGameException as e:
            self.stop(str(e))
            self.sparkle(e.code)
        finally:
            self.update_ui()
        """

    def timerEvent(self, event):
        """
        try:
            if event.timerId() == self.timer.timerId():
                self.engine.move()
            elif event.timerId() == self.acc_timer.timerId() and not self._difficulty['Freeze']:
                self.accelerate()
            elif event.timerId() == self.spark_timer.timerId():
                self.sparkle_step()
                self.update_ui()
            else:
                super(GameBox, self).timerEvent(event)
        except engine.StopGameException as e:
            self.stop(str(e))
            self.sparkle(e.code)
        finally:
            self.update_ui()
        """

    def paintEvent(self, event):
        """
        for i in range(config.BoxHeight):
            for j in range(config.BoxWidth):
                self.draw_square(j, i, self.engine.cell(i, j))
        """

    def update_ui(self):
        """
        if self.isStarted and not self.isPaused:
            self.set_status_message(f'Размер: {self.engine.length()}')
        self.update()
        """

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

        # self.statusbar.showMessage(messages)

        if index < len(self.status_labels):
            self.status_labels[index].setText(message)

    def clear_status_messages(self):
        self.set_status_messages(('', '', ''))

    def draw_square(self, left, top, sq_type):
        """ отрисовка квадратика """
        """
        w = left * self.scale_width()
        h = top * self.scale_height()

        painter = QPainter(self)

        if sq_type == config.FIELD_TYPE_NONE:
            painter.fillRect(w, h, self.scale_width(), self.scale_height(), QColor(config.Colors[sq_type]))
            return
        elif sq_type == config.FIELD_TYPE_BODY:
            color = QColor(self.body_gradient[self.engine.body_index(top, left)].get_hex())
        else:
            color = QColor(config.Colors[sq_type])

        painter.fillRect(w + 1, h + 1, self.scale_width() - 2, self.scale_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(w, h + self.scale_height() - 1, w, h)
        painter.drawLine(w, h, w + self.scale_width() - 1, h)

        painter.setPen(color.darker(150))
        painter.drawLine(w + 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + self.scale_height() - 1)
        painter.drawLine(w + self.scale_width() - 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + 1)
        """
