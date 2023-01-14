import os

APP_DATA_DIR = os.path.normpath(os.path.join(os.path.expanduser('~'), '.poker', 'app'))
PROFILES_DIR = f'{APP_DATA_DIR}/profile'
PARAMS_FILE = f'{APP_DATA_DIR}/params.json'
PROFILES_FILE = f'{APP_DATA_DIR}/profiles.json'
RES_DIR = 'resources'
MAIN_ICON = f'{RES_DIR}/app.ico'
BG_DIR = f'{RES_DIR}/background'
CARD_BACK_DIR = f'{RES_DIR}/back'
CARD_DECK_DIR = f'{RES_DIR}/deck'
FACE_DIR = f'{RES_DIR}/face'
SUITS_DIR = f'{RES_DIR}/suits'

DECK_TYPE = ('eng', 'rus', 'slav', 'sol', 'souv')  # типы внешних видов колод (так же называются папки с соотв. картинками)
DECK_NAMES = ('Буржуйская', 'Русская', 'Славянская', 'Пасьянсовая', 'Сувенирная')
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
FACE_SIZE = 128, 128        # width, height
USER_FACE_SIZE = 180, 180   # width, height
PLAYER_AREA_SIZE = 300, 200
INFO_AREA_SIZE = 500, 200
TABLE_AREA_SIZE = 500, 450

# Варианты начала игры:
#   0 - быстрый: без диалогов: игроки случайно; договоренности сохраненные/дефолтные
#   1 - показ только диалога выбора и настройки игроков; договоренности сохраненные/дефолтные
#   2 - показ только диалога настройки договоренностей; игроков накидает случайно
#   3 - показать оба диалога: игроков и договоренностей
GAME_START_TYPE_FAST = 0
GAME_START_TYPE_PLAYERS = 1
GAME_START_TYPE_AGREEMENTS = 2
GAME_START_TYPE_ALL = 3
GAME_START_TYPES = (
    ('Без вопросов', 'Не показывать никаких диалогов, а сразу начинать игру.<br>Договоренности будут взяты ранее '
                     'заданные.<br>Игроки добавятся случайным образом.'),
    ('Только выбор игроков', 'Будет показан только диалог выбора игроков.<br>Договоренности будут взяты ранее заданные.'),
    ('Только договоренности', 'Будет показан только диалог настройки договоренностей.<br>Игроки случайно.'),
    ('Все диалоги', 'Будут показаны оба диалога:<br>настройки договоренностей и выбора игроков.')
)

# ключи параметров темы оформления
# FONT_FAMILY = 'font_family'               # шрифт - только это пока под вопросом
# фон, цвет фона
BG_TEXTURE = 'bg_texture'                   # фоновый рисунок
BG_COLOR = 'bg_color'                       # основной цвет
BG_COLOR_2 = 'bg_color_2'                   # дополнительный цвет
BG_DISABLED = 'bg_disabled'                 # цевет неактивного элемента
BG_DARK_BTN = 'bg_dark_btn'                 # цвет кнопки "в темную"
BG_JOKER_LEAR_BTN = 'bg_joker_lear_btn'     # цвет кнопок выбора масти джокера
# цвета текста
COLOR_MAIN = 'color_main'                   # основной цвет (заказ, счет, имя пользователя и пр.)
COLOR_EXTRA = 'color_extra'                 # дополнительный (подсказка на столе, шапка таблицы и пр.)
COLOR_EXTRA_2 = 'color_extra_2'             # дополнительный еще (надписи на некоторых кнопках)
COLOR_DISABLED = 'color_disabled'           # цевет неактивного элемента
COLOR_GOOD = 'color_good'                   # цвет позитивных сообщений
COLOR_BAD = 'color_bad'                     # цвет негативных сообщений
COLOR_NEUTRAL = 'color_neutral'             # цвет нейтральных сообщений
COLOR_DARK_BTN = 'color_dark_btn'           # цвет кнопки "в темную"
# цвета надписей раздач
COLOR_DEAL_NORMAL = 'color_deal_normal'     # обычная
COLOR_DEAL_NOTRUMP = 'color_deal_notrump'   # бескозырка
COLOR_DEAL_DARK = 'color_deal_dark'         # темная
COLOR_DEAL_GOLD = 'color_deal_gold'         # золотая
COLOR_DEAL_MIZER = 'color_deal_mizer'       # мизер
COLOR_DEAL_BROW = 'color_deal_brow'         # лобовая
# цвета игроков в таблице хода игры
BG_PLAYER_1 = 'bg_player_1'
COLOR_PLAYER_1 = 'color_player_1'
BG_PLAYER_2 = 'bg_player_2'
COLOR_PLAYER_2 = 'color_player_2'
BG_PLAYER_3 = 'bg_player_3'
COLOR_PLAYER_3 = 'color_player_3'
BG_PLAYER_4 = 'bg_player_4'
COLOR_PLAYER_4 = 'color_player_4'
BG_TEXTURE_NOTHING = '< нет >'

DECORATION_THEMES = {
    'green': {
        BG_TEXTURE: f'{BG_DIR}/cards_cloth.jpg',
        BG_COLOR: 'DarkGreen',
        BG_COLOR_2: 'YellowGreen',
        BG_DISABLED: 'Gray',
        BG_DARK_BTN: 'DarkRed',
        BG_JOKER_LEAR_BTN: 'LightCyan',
        COLOR_MAIN: 'Aqua',
        COLOR_EXTRA: 'Yellow',
        COLOR_EXTRA_2: 'Purple',
        COLOR_DISABLED: 'DimGray',
        COLOR_GOOD: 'Lime',
        COLOR_BAD: 'Chocolate',
        COLOR_NEUTRAL: 'Gold',
        COLOR_DARK_BTN: 'Gold',
        COLOR_DEAL_NORMAL: 'LightCyan',
        COLOR_DEAL_NOTRUMP: 'Lime',
        COLOR_DEAL_DARK: 'Black',
        COLOR_DEAL_GOLD: 'Yellow',
        COLOR_DEAL_MIZER: 'Chocolate',
        COLOR_DEAL_BROW: 'salmon',
        BG_PLAYER_1: 'DarkOliveGreen',
        COLOR_PLAYER_1: 'Yellow',
        BG_PLAYER_2: 'Indigo',
        COLOR_PLAYER_2: 'Cyan',
        BG_PLAYER_3: 'Purple',
        COLOR_PLAYER_3: 'Honeydew',
        BG_PLAYER_4: 'DarkSlateGray',
        COLOR_PLAYER_4: 'Aqua'
    },
    'custom': {}
}

COLORS = tuple('aliceblue,antiquewhite,aqua,aquamarine,azure,beige,bisque,black,blanchedalmond,blue,blueviolet,brown,' \
    'burlywood,cadetblue,chartreuse,chocolate,coral,cornflowerblue,cornsilk,crimson,cyan,darkblue,darkcyan,darkgoldenrod,' \
    'darkgray,darkgreen,darkgrey,darkkhaki,darkmagenta,darkolivegreen,darkorange,darkorchid,darkred,darksalmon,' \
    'darkseagreen,darkslateblue,darkslategray,darkslategrey,darkturquoise,darkviolet,deeppink,deepskyblue,dimgray,dimgrey,' \
    'dodgerblue,firebrick,floralwhite,forestgreen,fuchsia,gainsboro,ghostwhite,gold,goldenrod,gray,grey,green,greenyellow,' \
    'honeydew,hotpink,indianred,indigo,ivory,khaki,lavender,lavenderblush,lawngreen,lemonchiffon,lightblue,lightcoral,' \
    'lightcyan,lightgoldenrodyellow,lightgray,lightgreen,lightgrey,lightpink,lightsalmon,lightseagreen,lightskyblue,' \
    'lightslategray,lightslategrey,lightsteelblue,lightyellow,lime,limegreen,linen,magenta,maroon,mediumaquamarine,' \
    'mediumblue,mediumorchid,mediumpurple,mediumseagreen,mediumslateblue,mediumspringgreen,mediumturquoise,mediumvioletred,' \
    'midnightblue,mintcream,mistyrose,moccasin,navajowhite,navy,oldlace,olive,olivedrab,orange,orangered,orchid,' \
    'palegoldenrod,palegreen,paleturquoise,palevioletred,papayawhip,peachpuff,peru,pink,plum,powderblue,purple,red,' \
    'rosybrown,royalblue,saddlebrown,salmon,sandybrown,seagreen,seashell,sienna,silver,skyblue,slateblue,slategray,' \
    'slategrey,snow,springgreen,steelblue,tan,teal,thistle,tomato,turquoise,violet,wheat,white,whitesmoke,yellow,' \
    'yellowgreen'.split(','))

THEME_CONTROLS_TITLE = {
    BG_TEXTURE: 'Текстура фона',
    BG_COLOR: 'Цвет фона',
    BG_COLOR_2: 'Цвет фона 2',
    BG_DISABLED: 'Фон неактивного\nэлемента',
    BG_DARK_BTN: 'Фон кнопки\nВ темную',
    BG_JOKER_LEAR_BTN: 'Фон кнопок\nвыбора масти джокера',
    COLOR_MAIN: 'Основной цвет',
    COLOR_EXTRA: 'Дополнительный цвет',
    COLOR_EXTRA_2: 'Дополнительный цвет 2',
    COLOR_DISABLED: 'Цвет неактивного\nэлемента',
    COLOR_GOOD: 'Цвет хорошего',
    COLOR_BAD: 'Цвет плохого',
    COLOR_NEUTRAL: 'Цвет нейтрального',
    COLOR_DARK_BTN: 'Цвет кнопки\nВ темную',
    COLOR_DEAL_NORMAL: 'Цвет обычной',
    COLOR_DEAL_NOTRUMP: 'Цвет бескозырки',
    COLOR_DEAL_DARK: 'Цвет темной',
    COLOR_DEAL_GOLD: 'Цвет золотой',
    COLOR_DEAL_MIZER: 'Цвет мизера',
    COLOR_DEAL_BROW: 'Цвет лобовой',
    BG_PLAYER_1: 'Фон игрок 1',
    COLOR_PLAYER_1: 'Цвет игрок 1',
    BG_PLAYER_2: 'Фон игрок 2',
    COLOR_PLAYER_2: 'Цвет игрок 2',
    BG_PLAYER_3: 'Фон игрок 3',
    COLOR_PLAYER_3: 'Цвет игрок 3',
    BG_PLAYER_4: 'Фон игрок 4',
    COLOR_PLAYER_4: 'Цвет игрок 4'
}