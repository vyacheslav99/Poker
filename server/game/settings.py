""" Базовые параметры игрового движка """

import os


# Пути, папки, файлы
DOCUMENT_ROOT = os.path.normpath(os.path.join(os.path.expanduser('~'), '.poker', 'server'))
PROFILES_DIR = os.path.join(DOCUMENT_ROOT, 'profiles')
PROFILE_DIR = os.path.join(PROFILES_DIR, '{profile_id}')
SAVE_DIR = os.path.join(PROFILE_DIR, 'save')  # формат pickle (предварительно, если ничто не помешает)
USER_PARAMS_FILE = os.path.join(PROFILE_DIR, 'params.conf')  # формат json

USER_DATABASE = {
    'sqlite': {
        'file': os.path.join(DOCUMENT_ROOT, 'users.sqlite')
    }
}
