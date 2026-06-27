import chess

EXACT = 0
LOWER = 1
UPPER = 2


class TTEntry:
    __slots__ = ("key", "depth", "score", "flag", "best_move")

    def __init__(self, key, depth, score, flag, best_move):
        self.key = key
        self.depth = depth
        self.score = score
        self.flag = flag
        self.best_move = best_move


class TranspositionTable:
    def __init__(self, max_entries=1000000):
        self.max_entries = max_entries
        self.table = {}

    def clear(self):
        self.table.clear()

    def get(self, board):
        key = board._transposition_key()
        entry = self.table.get(key)
        if entry and entry.key == key:
            return entry
        return None

    def store(self, board, depth, score, flag, best_move):
        key = board._transposition_key()
        self.table[key] = TTEntry(key, depth, score, flag, best_move)
        if len(self.table) > self.max_entries:
            items = list(self.table.items())
            self.table = dict(items[len(items) // 2:])
