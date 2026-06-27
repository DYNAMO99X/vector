import chess
import random
import time
from bot.evaluator import evaluate
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

    def _minimax(self, board, depth, alpha, beta):
        self.nodes_searched += 1

        if self._abort:
            return evaluate(board)

        if self._deadline and time.time() >= self._deadline:
            self._abort = True
            return evaluate(board)

        if depth == 0 or board.is_game_over():
            return evaluate(board)

        moves = list(board.legal_moves) if self.version == 0 else order_moves(board, list(board.legal_moves))

        for move in moves:
            if self._abort:
                break
            board.push(move)
            score = -self._minimax(board, depth - 1, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha
