from typing import List
from server.game_wrapper import GameWrapper


class Dispatcher:

    def __init__(self):
        self._games: List[GameWrapper] = []

    def on_close(self):
        for game in self._games:
            if not game.is_finished():
                game.save_game()