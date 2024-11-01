""" Константы игрового движка """

# уровни сложности игрка (ИИ)
DIF_EASY = 0
DIF_MEDIUM = 1
DIF_HARD = 2

DIFFICULTY_NAMES = ('Слабый', 'Средний', 'Сильный')

# уровни риска игрка (ИИ)
RISK_LVL_CAREFUL = 0    # Осторожный
RISK_LVL_MEDIUM = 1     # Умеренный
RISK_LVL_RISKY = 2      # Рискованный

RISK_LVL_NAMES = ('Осторожный', 'Умеренный', 'Рискованный')
RISK_BASE_COEFF = (1, 0, -1)

# типы игроков
PLAYER_TYPE_HUMAN = 0
PLAYER_TYPE_ROBOT = 1

# виды раздач
DEAL_NORMAL_ASC = 0     # Обычная возрастающая
DEAL_NORMAL_FULL = 1    # Обычная полная (вся колода)
DEAL_NORMAL_DESC = 2    # Обычная убывающая
DEAL_NO_TRUMP = 3       # Бескозырка
DEAL_DARK = 4           # Темная
DEAL_MIZER = 5          # Мизер
DEAL_GOLD = 6           # Золотая
DEAL_BROW = 7           # Лобовая

DEAL_NAMES = ('Возрастающая', 'Обычная', 'Убывающая', 'Бескозырка', 'Темная', 'Мизер', 'Золотая', 'Лобовая')

# варианты действий джокером
JOKER_TAKE = 0          # Забрать
JOKER_TAKE_BY_MAX = 1   # Забрать по старшей карте масти
JOKER_GIVE = 2          # Скинуть
# JOKER_TAKE_BY_MIN = 3   # Забрать по младшей карте масти

# Масти
LEAR_NOTHING = -1       # Нет масти (неопределена)
LEAR_HEARTS = 3         # Червы
LEAR_DIAMONDS = 2       # Бубны
LEAR_CLUBS = 1          # Крести
LEAR_SPADES = 0         # Пики

LEAR_SYMBOLS = ('♠', '♣', '♦', '♥')
LEAR_NAMES = ('Пика', 'Крестя', 'Бубна', 'Черва')

# Карты
# 6-10: числа
# 11 Jack (Валет), 12 Queen (Дама), 13 King (Король), 14 Ace (Туз)
# Joker (Джокер) - 7 пика
CARD_NAMES = tuple(str(i) for i in range(0, 11)) + ('Валет', 'Дама', 'Король', 'Туз')
CARD_LETTERS = tuple(str(i) for i in range(0, 11)) + ('В', 'Д', 'К', 'Т')

# флаги текущего состояния для внешних интерфейсов
EXT_STATE_DEAL = 0              # раздача карт
EXT_STATE_WALKS = 1             # делаем ходы в круге
EXT_STATE_LAP_PAUSE = 2         # подсчет итогов круга и пауза между кругами, чтобы дать человеку посмотреть итоги
EXT_STATE_ROUND_PAUSE = 3       # подсчет итогов раунда, пауза между раундами перед переходом к следующему, чтобы дать
                                #   человеку посмотреть итоги

# состояние по взяткам у игроков
TAKE_STATE_POOR = -1    # недобрал
TAKE_STATE_OK = 0       # взял свое
TAKE_STATE_OVERDO = 1   # перебрал

# флаги остановки игры
GAME_STOP_DEFER = 0
GAME_STOP_THROW = 1
