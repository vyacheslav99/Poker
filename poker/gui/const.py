import os

APP_DATA_DIR = os.path.normpath(os.path.join(os.path.expanduser('~'), '.poker', 'app'))
PROFILES_DIR = f'{APP_DATA_DIR}/profile'
PARAMS_FILE = f'{APP_DATA_DIR}/params.json'
PROFILES_FILE = f'{APP_DATA_DIR}/profiles.json'
RES_DIR = 'gui/resources'
MAIN_ICON = f'{RES_DIR}/app.ico'
BG_DIR = f'{RES_DIR}/background'
CARD_BACK_DIR = f'{RES_DIR}/back'
CARD_DECK_DIR = f'{RES_DIR}/deck'
FACE_DIR = f'{RES_DIR}/face'
SUITS_DIR = f'{RES_DIR}/suits'

DECK_TYPE = ('eng', 'rus', 'slav', 'sol', 'souv')  # типы внешних видов колод (так же называются папки с соотв. картинками)
LEARS = ('s', 'c', 'd', 'h')  # масти сокращенно (для формирования имени файла с картинкой карты)
CARDS = tuple(str(i) for i in range(0, 11)) + ('j', 'q', 'k', 'a')  # карты сокращенно (для формирования имени файла с картинкой карты)

ROBOTS = ('Адам Вест', 'Барт', 'Бендер', 'Бернс', 'Брайан', 'Бранниган', 'Гермес', 'Гомер', 'Джо Свонсон',
          'Зойдберг', 'Зубастик', 'Калькулон', 'Киф', 'Крис', 'Куагмаер', 'Лиза', 'Лила', 'Лоис', 'Мардж', 'Мэг',
          'Мэгги', 'Питер', 'Профессор', 'Стюи', 'Фрай', 'Эмми Вонг')

HUMANS = ('Мария', 'Хуана', 'Агата', 'Сильвия', 'Катя', 'Анна', 'Саманта', 'Жади', 'Алёна', 'Василиса')
CONGRATULATIONS = ('УРА, Товарищи!!!', 'Ай, молодца!', 'Учитесь, сынки!')

AREA_SIZE = 1300, 900
WINDOW_SIZE = 1400, 960
MAIN_WINDOW_TITLE = 'Расписной покер'

CARD_SIZE = 71, 96
CARD_SIDE_FACE = 0
CARD_SIDE_BACK = 1
CARD_OFFSET = 3, 3
CARD_BASE_Z_VALUE = 9999
FACE_SIZE = 128, 128
PLAYER_AREA_SIZE = 300, 200
INFO_AREA_SIZE = 500, 200
TABLE_AREA_SIZE = 500, 450
