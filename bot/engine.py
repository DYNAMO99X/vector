import chess
import random
import time
from bot.evaluator import evaluate
from bot.ordering import order_moves


class Engine:
    def __init__(self, depth=3, version=0):
        self.depth = depth
        self.version = version
        self.searching = False
        self.best_move = None
        self.nodes_searched = 0

    def find_move(self, board, max_time=None):
        if self.version == 0:
            return self._minimax_root(board, self.depth)

        self._deadline = time.time() + max_time if max_time else None

        best = None
        for d in range(1, self.depth + 1):
            if self._deadline and time.time() >= self._deadline:
                break
            best = self._minimax_root(board, d, previous_best=best)
        return best

    def _minimax_root(self, board, depth, previous_best=None):
        self.nodes_searched = 0
        best_score = -float("inf")
        best_move = None

        moves = order_moves(board, list(board.legal_moves), previous_best)

        for move in moves:
            board.push(move)
            score = -self._minimax(board, depth - 1, -float("inf"), float("inf"))
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(self, board, depth, alpha, beta):
        self.nodes_searched += 1

        if self._deadline and self.nodes_searched % 1024 == 0 and time.time() >= self._deadline:
            return evaluate(board)

        if depth == 0 or board.is_game_over():
            return evaluate(board)

        moves = list(board.legal_moves) if self.version == 0 else order_moves(board, list(board.legal_moves))

        for move in moves:
            board.push(move)
            score = -self._minimax(board, depth - 1, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha
