import logging

from typing import Optional

from configs import config
from modules.db import postgresql_connection
from server.dispatcher import Dispatcher


class Application:

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Application, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        self._dispatcher: Optional[Dispatcher] = None
        self._db: Optional[postgresql_connection] = None

    def create_app(self):
        self._dispatcher = Dispatcher()
        logging.info('Connecting to database...')
        self._db = postgresql_connection(config.DATABASE)

    def close_app(self):
        if self._dispatcher:
            logging.info('Dumping games...')
            self._dispatcher.on_close()

    @property
    def db(self):
        return self._db

    @property
    def dispatcher(self):
        return self._dispatcher


app = Application()