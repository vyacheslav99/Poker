import logging
import uuid

from core.engine import Engine


class GameWrapper:

    def __init__(self, engine: Engine, uid: str = None):
        self.uid = uid or uuid.uuid4().hex
        self._engine: Engine = engine

    def is_finished(self) -> bool:
        # todo: сделать реализацию
        return False

    @property
    def engine(self) -> Engine:
        return self._engine

    def save_game(self):
        logging.debug(f'Saving game: {self.uid}')