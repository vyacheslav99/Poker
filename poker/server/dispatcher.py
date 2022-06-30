from typing import List
from server.game_wrapper import GameWrapper


class Dispatcher:

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Dispatcher, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        self._games: List[GameWrapper] = []

    def on_close(self):
        for game in self._games:
            if not game.is_finished():
                game.save_game()