import chess
from bot.evaluator import PIECE_VALUES


def mvv_lva(board, move):
    victim = board.piece_at(move.to_square)
    attacker = board.piece_at(move.from_square)
    if victim is None or attacker is None:
        return 0
    return PIECE_VALUES[victim.piece_type] * 10 - PIECE_VALUES[attacker.piece_type]


def score_move(board, move):
    if board.is_en_passant(move):
        return PIECE_VALUES[chess.PAWN] * 10 + 1000
    victim = board.piece_at(move.to_square)
    if victim is not None:
        attacker = board.piece_at(move.from_square)
        if attacker is None:
            return 0
        return PIECE_VALUES[victim.piece_type] * 10 - PIECE_VALUES[attacker.piece_type] + 1000
    if board.is_castling(move):
        return 800
    return 0


def order_moves(board, moves, best_move=None):
    scored = []
    for move in moves:
        score = 0
        if best_move and move == best_move:
            score = 100000
        else:
            score = score_move(board, move)
        scored.append((score, move))
    scored.sort(key=lambda x: -x[0])
    return [m for _, m in scored]
