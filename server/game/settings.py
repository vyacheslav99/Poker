""" Базовые параметры игрового движка """

import os


DOCUMENT_ROOT = os.path.normpath(os.path.join(os.path.expanduser('~'), '.poker', 'server'))
DATA_DIR = os.path.join(DOCUMENT_ROOT, 'data')
FILESTORE_DIR = os.path.join(DATA_DIR, 'files')

USER_DATABASE_DRIVER = 'sqlite'
USER_DATABASE = {
    'sqlite': {
        'database': os.path.join(DOCUMENT_ROOT, 'users.sqlite')
    }
}
