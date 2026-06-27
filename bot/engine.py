import chess
import random
import time
from bot.evaluator import evaluate, evaluate_mark3, PIECE_VALUES, is_endgame
from bot.ordering import order_moves
from bot.book import OpeningBook


class Engine:
    def __init__(self, depth=3, version=0, book_enabled=True):
        self.depth = depth
        self.version = version
        self.book_enabled = book_enabled
        self._book = OpeningBook()
        self.searching = False
        self.best_move = None
        self.nodes_searched = 0

    def find_move(self, board, max_time=None):
        if self.book_enabled:
            book_move = self._book.get_move(board)
            if book_move is not None:
                return book_move

        self._deadline = time.time() + max_time if max_time else None
        self._abort = False

        if self.version == 0:
            return self._minimax_root(board, self.depth)

        best = None
        for d in range(1, self.depth + 1):
            if self._abort:
                break
            best = self._minimax_root(board, d, previous_best=best)
        return best

    def _minimax_root(self, board, depth, previous_best=None):
        self.nodes_searched = 0
        best_score = -float("inf")
        best_move = None

        moves = order_moves(board, list(board.legal_moves), previous_best)

        for move in moves:
            if self._abort:
                break
            board.push(move)
            score = -self._minimax(board, depth - 1, -float("inf"), float("inf"))
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        if best_move is None and moves:
            best_move = moves[0]

        return best_move

    def _quiesce(self, board, alpha, beta):
        self.nodes_searched += 1

        if self._abort:
            return evaluate(board)

        if self._deadline and time.time() >= self._deadline:
            self._abort = True
            return evaluate(board)

        eval_fn = evaluate_mark3 if self.version == 2 else evaluate
        stand_pat = eval_fn(board)

        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        in_check = board.is_check()
        for move in board.legal_moves:
            if not in_check and not board.is_capture(move):
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

    def _minimax(self, board, depth, alpha, beta):
        self.nodes_searched += 1

        if self._abort:
            return evaluate(board)

        if self._deadline and time.time() >= self._deadline:
            self._abort = True
            return evaluate(board)

        if depth == 0 or board.is_game_over():
            if self.version >= 1:
                return self._quiesce(board, alpha, beta)
            return evaluate(board)

        in_check = board.is_check()

        # Null-move pruning (Mark 2+ only; skip in check, endgame, or shallow depth)
        if self.version >= 1 and depth >= 3 and not in_check and not is_endgame(board):
            board.push(chess.Move.null())
            score = -self._minimax(board, depth - 2, -beta, -beta + 1)
            board.pop()
            if score >= beta:
                return beta

        moves = list(board.legal_moves) if self.version == 0 else order_moves(board, list(board.legal_moves))

        for i, move in enumerate(moves):
            if self._abort:
                break
            board.push(move)
            # PVS: full window on first move, zero window on the rest
            if i == 0:
                score = -self._minimax(board, depth - 1, -beta, -alpha)
            else:
                score = -self._minimax(board, depth - 1, -alpha - 1, -alpha)
                if score > alpha and score < beta:
                    score = -self._minimax(board, depth - 1, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha
