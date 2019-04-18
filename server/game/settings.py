""" Базовые параметры игрового движка """

import os


DOCUMENT_ROOT = os.path.normpath(os.path.join(os.path.expanduser('~'), '.poker', 'server'))

USER_DATABASE = {
    'sqlite': {
        'file': os.path.join(DOCUMENT_ROOT, 'users.sqlite')
    }
}
