import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0,
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0,
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20,
]

KING_ENDGAME_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50,
]

PST = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}


def is_endgame(board):
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
    total_pieces = len(board.piece_map())
    return queens == 0 or total_pieces <= 10


def evaluate(board):
    if board.is_checkmate():
        return -30000 if board.turn else 30000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    eg = is_endgame(board)

    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type]
        sq_idx = square if piece.color == chess.WHITE else chess.square_mirror(square)
        pst = PST[piece.piece_type]

        if piece.piece_type == chess.KING and eg:
            pst = KING_ENDGAME_TABLE

        positional = pst[sq_idx]

        if piece.color == chess.WHITE:
            score += value + positional
        else:
            score -= value + positional

    return score


def is_passed_pawn(board, square, color):
    pawn = board.piece_at(square)
    if pawn is None or pawn.piece_type != chess.PAWN:
        return False
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    direction = 1 if color == chess.WHITE else -1
    enemy = not color

    for f in (file - 1, file, file + 1):
        if f < 0 or f > 7:
            continue
        for r in range(rank + direction, 8 if color == chess.WHITE else -1, direction):
            target = chess.square(f, r)
            p = board.piece_at(target)
            if p and p.piece_type == chess.PAWN and p.color == enemy:
                return False
    return True


def passed_pawn_bonus(board, color):
    bonus = 0
    for sq in board.pieces(chess.PAWN, color):
        if is_passed_pawn(board, sq, color):
            rank = chess.square_rank(sq)
            bonus += 20 + rank * 20 if color == chess.WHITE else 20 + (7 - rank) * 20
    return bonus


def count_doubled_pawns(board, color):
    files = {}
    for sq in board.pieces(chess.PAWN, color):
        f = chess.square_file(sq)
        files[f] = files.get(f, 0) + 1
    return sum(c - 1 for c in files.values())


def count_isolated_pawns(board, color):
    files = {chess.square_file(sq) for sq in board.pieces(chess.PAWN, color)}
    isolated = 0
    for sq in board.pieces(chess.PAWN, color):
        f = chess.square_file(sq)
        if f - 1 not in files and f + 1 not in files:
            isolated += 1
    return isolated


def king_safety(board, color):
    king_sq = board.king(color)
    if king_sq is None:
        return 0
    kf = chess.square_file(king_sq)
    kr = chess.square_rank(king_sq)
    direction = 1 if color == chess.WHITE else -1
    shield = 0
    for df in (-1, 0, 1):
        for dr in (direction, direction * 2):
            f = kf + df
            r = kr + dr
            if 0 <= f < 8 and 0 <= r < 8:
                sq = chess.square(f, r)
                p = board.piece_at(sq)
                if p and p.piece_type == chess.PAWN and p.color == color:
                    shield += 1
    return shield * 15


def rook_open_file_bonus(board, color):
    bonus = 0
    for sq in board.pieces(chess.ROOK, color):
        f = chess.square_file(sq)
        friendly = any(chess.square_file(s) == f for s in board.pieces(chess.PAWN, color))
        enemy = any(chess.square_file(s) == f for s in board.pieces(chess.PAWN, not color))
        if not friendly and not enemy:
            bonus += 20
        elif not friendly:
            bonus += 10
    return bonus


def bishop_pair_bonus(board, color):
    return 30 if len(board.pieces(chess.BISHOP, color)) >= 2 else 0


def mobility(board, color):
    weights = {chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 2, chess.QUEEN: 1}
    total = 0
    for pt, w in weights.items():
        for sq in board.pieces(pt, color):
            total += len(board.attacks(sq)) * w
    return total


def king_tropism(board, color):
    enemy_king = board.king(not color)
    if enemy_king is None:
        return 0
    total = 0
    for pt in (chess.KNIGHT, chess.BISHOP, chess.QUEEN):
        for sq in board.pieces(pt, color):
            dist = chess.square_distance(sq, enemy_king)
            total += (7 - dist) * 2
    return total


def evaluate_mark3(board):
    if board.is_checkmate():
        return -30000 if board.turn else 30000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    eg = is_endgame(board)

    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type]
        sq_idx = square if piece.color == chess.WHITE else chess.square_mirror(square)
        pst = PST[piece.piece_type]
        if piece.piece_type == chess.KING and eg:
            pst = KING_ENDGAME_TABLE
        score += (value + pst[sq_idx]) if piece.color == chess.WHITE else -(value + pst[sq_idx])

    for color, sign in ((chess.WHITE, 1), (chess.BLACK, -1)):
        score += sign * passed_pawn_bonus(board, color)
        score -= sign * count_doubled_pawns(board, color) * 15
        score -= sign * count_isolated_pawns(board, color) * 20
        score += sign * rook_open_file_bonus(board, color)
        score += sign * bishop_pair_bonus(board, color)
        if not eg:
            score += sign * king_safety(board, color)
            score += sign * king_tropism(board, color)

    if not eg:
        score += (mobility(board, chess.WHITE) - mobility(board, chess.BLACK)) * 2

    return score
