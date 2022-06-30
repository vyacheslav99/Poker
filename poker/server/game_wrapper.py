from core.engine import Engine


class GameWrapper:

    def __init__(self, engine: Engine):
        self._engine: Engine = engine