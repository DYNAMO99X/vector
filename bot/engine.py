import chess
import random
import time
from bot.evaluator import evaluate, evaluate_mark3, PIECE_VALUES, is_endgame, see
from bot.ordering import order_moves, History, KillerMoves
from bot.book import OpeningBook
from bot.transposition import TranspositionTable, EXACT, LOWER, UPPER


class Engine:
    def __init__(self, depth=3, version=0, book_enabled=True, book_path=None):
        self.depth = depth
        self.version = version
        self.book_enabled = book_enabled
        self._book = OpeningBook(book_path)
        self.tt = TranspositionTable()
        self.history = History()
        self.killers = KillerMoves()
        self.searching = False
        self.best_move = None
        self.nodes_searched = 0

    def update_book_path(self, book_path):
        self._book = OpeningBook(book_path)

    def find_move(self, board, max_time=None):
        if self.book_enabled:
            book_move = self._book.get_move(board)
            if book_move is not None:
                return book_move

        self._deadline = time.time() + max_time if max_time else None
        self._abort = False
        self.tt.clear()
        self.history.age()
        self.killers.clear()

        if self.version == 0:
            return self._minimax_root(board, self.depth)[0]

        best_move = None
        best_score = None
        for d in range(1, self.depth + 1):
            if self._abort:
                break
            best_move, best_score = self._minimax_root(board, d, previous_best=best_move, prev_score=best_score)
        return best_move

    def _minimax_root(self, board, depth, previous_best=None, prev_score=None):
        self.nodes_searched = 0
        best_score = -float("inf")
        best_move = None

        tt_entry = self.tt.get(board)
        tt_move = tt_entry.best_move if tt_entry else None
        see_fn = see if self.version >= 4 else None
        moves = order_moves(board, list(board.legal_moves), tt_move or previous_best, self.history, self.killers, ply=0, see_fn=see_fn)

        alpha = -float("inf")
        beta = float("inf")
        use_aspiration = prev_score is not None and depth >= 3 and self.version >= 1
        if use_aspiration:
            alpha = prev_score - 50
            beta = prev_score + 50

        for move in moves:
            if self._abort:
                break
            board.push(move)
            if use_aspiration:
                score = -self._minimax(board, depth - 1, -beta, -alpha, ply=1)
                if score <= alpha or score >= beta:
                    use_aspiration = False
                    score = -self._minimax(board, depth - 1, -float("inf"), float("inf"), ply=1)
            else:
                score = -self._minimax(board, depth - 1, -float("inf"), float("inf"), ply=1)
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        if best_move is None and moves:
            best_move = moves[0]

        return best_move, best_score

    def _quiesce(self, board, alpha, beta):
        self.nodes_searched += 1

        eval_fn = evaluate_mark3 if self.version >= 2 else evaluate

        if self._abort:
            return eval_fn(board)

        if self._deadline and time.time() >= self._deadline:
            self._abort = True
            return eval_fn(board)

        stand_pat = eval_fn(board)

        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        in_check = board.is_check()
        for move in board.legal_moves:
            if not in_check and not board.is_capture(move):
                continue
            # SEE pruning (Mark 5): skip losing captures
            if self.version >= 4 and not in_check and not board.is_en_passant(move):
                if see(board, move.to_square, board.turn) < 0:
                    continue
            victim = board.piece_at(move.to_square)
            if victim and stand_pat + PIECE_VALUES[victim.piece_type] + 200 < alpha:
                continue
            board.push(move)
            score = -self._quiesce(board, -beta, -alpha)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def _minimax(self, board, depth, alpha, beta, ply=0):
        self.nodes_searched += 1

        eval_fn = evaluate_mark3 if self.version >= 2 else evaluate

        if self._abort:
            return evaluate(board)

        if self._deadline and time.time() >= self._deadline:
            self._abort = True
            return evaluate(board)

        if depth <= 0 or board.is_game_over():
            if self.version >= 1:
                return self._quiesce(board, alpha, beta)
            return eval_fn(board)

        # TT probe (Mark 2+ only)
        tt_entry = self.tt.get(board) if self.version >= 1 else None
        tt_move = tt_entry.best_move if tt_entry else None
        if tt_entry and tt_entry.depth >= depth and self.version >= 1:
            if tt_entry.flag == EXACT:
                return tt_entry.score
            if tt_entry.flag == LOWER:
                alpha = max(alpha, tt_entry.score)
            elif tt_entry.flag == UPPER:
                beta = min(beta, tt_entry.score)
            if alpha >= beta:
                return tt_entry.score

        original_alpha = alpha

        in_check = board.is_check()

        # Null-move pruning (Mark 2+ only; skip in check, endgame, shallow depth, or unbounded window)
        if self.version >= 1 and depth >= 3 and not in_check and not is_endgame(board) and beta != float("inf"):
            board.push(chess.Move.null())
            score = -self._minimax(board, depth - 2, -beta, -beta + 1, ply + 1)
            board.pop()
            if score >= beta:
                return beta

        # Razoring (Mark 5): prune shallow nodes when eval can't reach alpha
        if self.version >= 4 and depth <= 2 and not in_check and alpha != -float("inf"):
            razor_margin = 300 if depth == 1 else 200
            razor_eval = eval_fn(board)
            if razor_eval + razor_margin < alpha:
                return razor_eval

        # IID (Mark 5): reduced-depth search to seed TT move when none exists
        if self.version >= 4 and tt_move is None and depth >= 3:
            iid_depth = max(1, depth // 2)
            self._minimax(board, iid_depth, alpha, beta, ply)
            iid_tt = self.tt.get(board)
            if iid_tt and iid_tt.best_move:
                tt_move = iid_tt.best_move

        see_fn = see if self.version >= 4 else None
        if self.version == 0:
            moves = list(board.legal_moves)
        else:
            moves = order_moves(board, list(board.legal_moves), tt_move, self.history, self.killers, ply, see_fn)

        best_move = None
        for i, move in enumerate(moves):
            if self._abort:
                break

            is_quiet = not board.is_capture(move) and not board.is_en_passant(move) and not board.is_castling(move) and not move.promotion is not None

            # Futility pruning (Mark 5): skip quiet moves that can't reach alpha
            if self.version >= 4 and depth <= 2 and is_quiet and not in_check and i >= 1:
                if not board.gives_check(move):
                    futility_margin = 200 if depth == 1 else 150
                    if eval_fn(board) + futility_margin <= alpha:
                        continue

            board.push(move)

            extension = 1 if board.is_check() else 0

            # LMR (Mark 2+)
            do_lmr = self.version >= 1 and depth >= 3 and i >= 3 and is_quiet and not in_check
            if do_lmr:
                hist_val = self.history.get(move.from_square, move.to_square)
                r = 1
                if i >= 6:
                    r = 2
                if hist_val <= 0:
                    r += 1
                reduced = max(1, depth - 1 - r + extension)
                score = -self._minimax(board, reduced, -alpha - 1, -alpha, ply + 1)
                if score > alpha:
                    score = -self._minimax(board, depth - 1 + extension, -beta, -alpha, ply + 1)
            elif i == 0:
                score = -self._minimax(board, depth - 1 + extension, -beta, -alpha, ply + 1)
            else:
                # PVS
                score = -self._minimax(board, depth - 1 + extension, -alpha - 1, -alpha, ply + 1)
                if score > alpha and score < beta:
                    score = -self._minimax(board, depth - 1 + extension, -beta, -alpha, ply + 1)

            board.pop()

            if score > alpha:
                alpha = score
                best_move = move
            if score >= beta:
                if is_quiet and best_move:
                    self.history.update(move.from_square, move.to_square, depth)
                    self.killers.store(ply, move)
                break

        # TT store (Mark 2+ only)
        if self.version >= 1:
            flag = EXACT
            if alpha <= original_alpha:
                flag = UPPER
            elif alpha >= beta:
                flag = LOWER
            self.tt.store(board, depth, alpha, flag, best_move)

        return alpha
