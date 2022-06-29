import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from gui import const
from core import const as core_const


class QCard(QGraphicsPixmapItem):

    def __init__(self, app, card, player, deck, back, removable=True, tooltip=None, replace_tooltip=False):
        super(QCard, self).__init__()

        self.app = app
        self.card = card
        self.player = player
        self.deck = deck
        self.back = back
        self.removable = removable
        self._tooltip = tooltip
        self.replace_tooltip = replace_tooltip
        self.side = None

        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(const.CARD_BASE_Z_VALUE)
        self.set_std_shadow()

        self.back = QPixmap(f'{const.CARD_BACK_DIR}/{self.back}.bmp')
        if card.joker:
            self.face = QPixmap(f'{const.CARD_DECK_DIR}/{self.deck}/j.bmp')
        else:
            self.face = QPixmap(f'{const.CARD_DECK_DIR}/{self.deck}/{const.CARDS[self.card.value]}{const.LEARS[self.card.lear]}.bmp')

    def turn_face_up(self):
        self.side = const.CARD_SIDE_FACE
        self.setPixmap(self.face)
        self.set_tooltip()

        if self.player:
            self.setCursor(Qt.PointingHandCursor)

    def turn_back_up(self):
        self.side = const.CARD_SIDE_BACK
        self.setPixmap(self.back)
        self.setCursor(Qt.ArrowCursor)
        self.setToolTip('')

    def is_face_up(self):
        return self.side == const.CARD_SIDE_FACE

    def set_tooltip(self):
        if self.replace_tooltip and self._tooltip:
            val = self._tooltip
        else:
            c = 'red' if self.card.lear > 1 else 'navy'
            val = f'{core_const.CARD_NAMES[self.card.value]} <span style="color:{c}">{core_const.LEAR_SYMBOLS[self.card.lear]}</span>'
            if self.card.joker:
                val = f'Джокер ({val})'
            if self._tooltip:
                val = f'{self._tooltip} {val}'

        self.setToolTip(val)

    def set_color_shadow(self):
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(30)
        sh.setOffset(5)
        sh.setColor(Qt.green)
        self.setGraphicsEffect(sh)

    def set_std_shadow(self):
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(50)
        self.setGraphicsEffect(sh)

    def mousePressEvent(self, e):
        if self.player and self.is_face_up():
            self.app.card_click(self)

        super(QCard, self).mousePressEvent(e)


class Face(QGraphicsPixmapItem):

    def __init__(self, player):
        super(Face, self).__init__()
        self.player = player
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player):
        self._player = player

        if player.avatar and os.path.exists(f'{const.PROFILES_DIR}/{player.uid}/{player.avatar}'):
            self.setPixmap(QPixmap(f'{const.PROFILES_DIR}/{player.uid}/{player.avatar}'))
        elif os.path.exists(f'{const.FACE_DIR}/{self._player.name}.bmp'):
            self.setPixmap(QPixmap(f'{const.FACE_DIR}/{self._player.name}.bmp'))
        else:
            self.setPixmap(QPixmap(f'{const.FACE_DIR}/noImage.png'))


class Face2(QPixmap):

    def __init__(self, player):
        self._player = player

        if player.avatar and os.path.exists(f'{const.PROFILES_DIR}/{player.uid}/{player.avatar}'):
            self._image_path = f'{const.PROFILES_DIR}/{player.uid}/{player.avatar}'
        elif os.path.exists(f'{const.FACE_DIR}/{self._player.name}.bmp'):
            self._image_path = f'{const.FACE_DIR}/{self._player.name}.bmp'
        else:
            self._image_path = f'{const.FACE_DIR}/noImage.png'

        super(Face2, self).__init__(self._image_path)

    @property
    def player(self):
        return self._player

    @property
    def image_path(self):
        return self._image_path


class Avatar(QPixmap):

    def __init__(self, uid=None, name=None):
        if uid and name and os.path.exists(f'{const.PROFILES_DIR}/{uid}/{name}'):
            self._image_path = f'{const.PROFILES_DIR}/{uid}/{name}'
        elif os.path.exists(f'{const.FACE_DIR}/{name}.bmp'):
            self._image_path = f'{const.FACE_DIR}/{name}.bmp'
        else:
            self._image_path = f'{const.FACE_DIR}/noImage.png'

        super(Avatar, self).__init__(self._image_path)

    @property
    def image_path(self):
        return self._image_path


class Lear(QGraphicsPixmapItem):

    def __init__(self, lear):
        super(Lear, self).__init__()
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        if lear == core_const.LEAR_NOTHING:
            self.setPixmap(QPixmap(f'{const.SUITS_DIR}/n.png'))
            self.setToolTip('Козырь: нет')
        else:
            self.setPixmap(QPixmap(f'{const.SUITS_DIR}/{const.LEARS[lear]}.png'))
            self.setToolTip(f'Козырь: {core_const.LEAR_NAMES[lear]}')


class Area(QGraphicsRectItem):

    def __init__(self, parent, size):
        super(Area, self).__init__()
        self.parent = parent
        self.setRect(QRectF(0, 0, size[0], size[1]))
        color = QColor(Qt.black)
        color.setAlpha(50)
        brush = QBrush(color)
        self.setBrush(brush)
        self.setPen(QPen(Qt.black))
        self.setZValue(-1)


class GridMoneyItemDelegate(QItemDelegate):

    def __init__(self, parent, bg_color=None):
        self._bg_color = bg_color

        super(GridMoneyItemDelegate, self).__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        value = index.model().data(index, Qt.EditRole)

        if value is not None and isinstance(value, (int, float)):
            if self._bg_color:
                painter.setBrush(QBrush(QColor(self._bg_color), Qt.SolidPattern))
                painter.drawRect(option.rect.x() - 1, option.rect.y() - 1, option.rect.width() + 1, option.rect.height() + 1)

            curr_uid = self.get_uid()
            uid = index.siblingAtColumn(0).data(Qt.WhatsThisRole)
            font = painter.font()
            font.setBold(uid is not None and curr_uid is not None and uid == curr_uid)
            painter.setFont(font)

            money = '{0:.2f}'.format(value)
            rub, kop = money.split('.')
            painter.drawText(option.rect, Qt.AlignRight | Qt.AlignVCenter, f' {rub}р {kop}к ')
        else:
            super(GridMoneyItemDelegate, self).paint(painter, option, index)

    def get_uid(self):
        grid = self.parent()
        if grid:
            form = grid.parent()
            if form:
                return form._curr_uid

        return None
