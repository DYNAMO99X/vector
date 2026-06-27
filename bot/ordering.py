import chess
from bot.evaluator import PIECE_VALUES


def see(board, square, side):
    """Wrapper to avoid circular import — delegates to evaluator.see."""
    from bot.evaluator import see as _see
    return _see(board, square, side)


class History:
    def __init__(self):
        self.table = [[0] * 64 for _ in range(64)]

    def get(self, from_sq, to_sq):
        return self.table[from_sq][to_sq]

    def update(self, from_sq, to_sq, depth):
        self.table[from_sq][to_sq] += depth * depth

    def clear(self):
        self.table = [[0] * 64 for _ in range(64)]

    def age(self):
        for i in range(64):
            row = self.table[i]
            for j in range(64):
                row[j] //= 2


class KillerMoves:
    def __init__(self, max_ply=64):
        self.slots = [[None, None] for _ in range(max_ply)]

    def store(self, ply, move):
        if move == self.slots[ply][0]:
            return
        self.slots[ply][1] = self.slots[ply][0]
        self.slots[ply][0] = move

    def is_killer(self, ply, move):
        return move == self.slots[ply][0] or move == self.slots[ply][1]

    def get_bonus(self, ply, move):
        if move == self.slots[ply][0]:
            return 500
        if move == self.slots[ply][1]:
            return 300
        return 0

    def clear(self):
        self.slots = [[None, None] for _ in range(len(self.slots))]


def mvv_lva(board, move):
    victim = board.piece_at(move.to_square)
    attacker = board.piece_at(move.from_square)
    if victim is None or attacker is None:
        return 0
    return PIECE_VALUES[victim.piece_type] * 10 - PIECE_VALUES[attacker.piece_type]


def score_move(board, move, history=None, killers=None, ply=0, see_fn=None):
    if board.is_en_passant(move):
        return PIECE_VALUES[chess.PAWN] * 10 + 1000
    victim = board.piece_at(move.to_square)
    if victim is not None:
        if see_fn:
            see_score = see_fn(board, move.to_square, board.turn)
            return see_score + 1000
        attacker = board.piece_at(move.from_square)
        if attacker is None:
            return 0
        return PIECE_VALUES[victim.piece_type] * 10 - PIECE_VALUES[attacker.piece_type] + 1000
    if board.is_castling(move):
        return 800
    bonus = 0
    if killers:
        bonus += killers.get_bonus(ply, move)
    if history:
        bonus += history.get(move.from_square, move.to_square) // 10
    return bonus


def order_moves(board, moves, best_move=None, history=None, killers=None, ply=0, see_fn=None):
    scored = []
    for move in moves:
        score = 0
        if best_move and move == best_move:
            score = 100000
        else:
            score = score_move(board, move, history, killers, ply, see_fn)
        scored.append((score, move))
    scored.sort(key=lambda x: -x[0])
    return [m for _, m in scored]
