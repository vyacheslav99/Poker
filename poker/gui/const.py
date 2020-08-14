import os
from PyQt5.QtCore import *

APP_DATA_DIR = os.path.normpath(os.path.join(os.path.expanduser('~'), '.poker', 'app'))
RES_DIR = 'gui/resources'
MAIN_ICON = f'{RES_DIR}/app.ico'
BG_DIR = f'{RES_DIR}/background'
CARD_BACK_DIR = f'{RES_DIR}/back'
CARD_DECK_DIR = f'{RES_DIR}/deck'
FACE_DIR = f'{RES_DIR}/face'

DECK_TYPE = ('eng', 'rus', 'slav', 'sol', 'souv')  # типы внешних видов колод (так же называются папки с соотв. картинками)
LEARS = ('s', 'c', 'd', 'h')  # масти сокращенно (для формирования имени файла с картинкой карты)

ROBOTS = ('Адам Вест', 'Барт', 'Бендер', 'Бёрнс', 'Брайан', 'Бранниган', 'Гермес', 'Гомер', 'Джо Свонсон',
          'Зойдберг', 'Зубастик', 'Калькулон', 'Киф', 'Крис', 'Куагмаер', 'Лиза', 'Лила', 'Лоис', 'Мардж', 'Мэг',
          'Мэгги', 'Питер', 'Профессор', 'Стюи', 'Фрай', 'Эмми Вонг')

HUMANS = ('Чубрик', 'Чел', 'Колян', 'Чувак', 'Толик', 'Маня', 'Фекла', 'Вася', 'Ваня', 'Дуня')

AREA_SIZE = 1300, 900
WINDOW_SIZE = 1400, 960
MAIN_WINDOW_TITLE = 'Расписной покер'

CARD_DIMENSIONS = QSize(71, 96)
CARD_RECT = QRect(0, 0, 71, 96)
CARD_SPACING_X = 90
CARD_SIDE_FACE = 0
CARD_SIDE_BACK = 1
