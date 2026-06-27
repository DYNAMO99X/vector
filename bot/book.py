import chess
import chess.polyglot
import random
import os

BOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "books")
DEFAULT_BOOK = os.path.join(BOOKS_DIR, "komodo.bin")


class OpeningBook:
    def __init__(self, path=None):
        self.path = path or DEFAULT_BOOK

    def get_move(self, board):
        try:
            with chess.polyglot.open_reader(self.path) as reader:
                entries = list(reader.find_all(board))
        except FileNotFoundError:
            return None

        if not entries:
            return None

        total = sum(e.weight for e in entries)
        pick = random.randint(0, total)
        cumulative = 0
        for e in entries:
            cumulative += e.weight
            if pick < cumulative:
                return e.move
        return entries[-1].move
