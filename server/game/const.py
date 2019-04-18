import os


DOCUMENT_ROOT = os.path.normpath(os.path.join(os.path.expanduser('~'), '.poker', 'server'))

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