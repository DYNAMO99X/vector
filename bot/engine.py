import chess
import random
from bot.evaluator import evaluate


class Engine:
    def __init__(self, depth=3):
        self.depth = depth
        self.searching = False
        self.best_move = None
        self.nodes_searched = 0

    def find_move(self, board):
        return self._minimax_root(board, self.depth)

    def _minimax_root(self, board, depth):
        self.nodes_searched = 0
        best_score = -float("inf")
        best_move = None

        for move in board.legal_moves:
            board.push(move)
            score = -self._minimax(board, depth - 1, -float("inf"), float("inf"))
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(self, board, depth, alpha, beta):
        self.nodes_searched += 1

        if depth == 0 or board.is_game_over():
            return evaluate(board)

        for move in board.legal_moves:
            board.push(move)
            score = -self._minimax(board, depth - 1, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha
