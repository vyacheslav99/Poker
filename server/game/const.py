""" Константы игрового движка """

# уровни сложности игрка (ИИ)
DIF_EASY = 0
DIF_MEDIUM = 1
DIF_HARD = 2

# уровни риска игрка (ИИ)
RISK_LVL_CAREFUL = 0    # Осторожный
RISK_LVL_MEDIUM = 1     # Умеренный
RISK_LVL_RISKY = 2      # Рискованный

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

# варианты действий джокером
JOKER_AS_CARD = 0       # Выдать за карту
JOKER_BIGEST = 1        # Как самая большая карта (т.е. бьет все и всегда, вариант "Забираю!")
JOKER_SMALLEST = 2      # Как самая маленькая карта (т.е. не побъет никогда, вариант "Скидываю!")
JOKER_TAKE_BY_MAX = 3   # Забрать по старшей карте масти
JOKER_TAKE_BY_MIN = 4   # Забрать по младшей карте масти

# Масти
LEAR_NOTHING = -1       # Нет масти (неопределена)
LEAR_HEARTS = 0         # Червы
LEAR_DIAMONDS = 1       # Бубны
LEAR_CLUBS = 2          # Крести
LEAR_SPADES = 3         # Пики

LEAR_SYMBOLS = ('♥', '♦', '♣', '♠')
LEAR_NAMES = ('Черва', 'Бубна', 'Крестя', 'Пика')

# Карты
# 6-10: числа
# 11 Jack (Валет), 12 Queen (Дама), 13 King (Король), 14 Ace (Туз)
# 7 - Joker (major): Джокер (старший) (7 пика)
CARD_NAMES = tuple(str(i) for i in range(6, 11)) + ('Валет', 'Дама', 'Король', 'Туз')

# Текущие цели ИИ (это пока не ясно, просто портировано с делфей. Как дойду до этого места в реализации, разберусь)
AI_GOAL_TAKE = 0        # Брать
AI_GOAL_PASS = 1        # Пропускать
AI_GOAL_LURE = 2        # Подбросить, отдать (приманка)
AI_GOAL_WASTE = 3       # Сбросить, скинуть
