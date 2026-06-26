import chess
import chess.pgn
import time
import constants


PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}


class Game:
    def __init__(self, time_minutes=10, time_increment=0):
        self.board = chess.Board()
        self.player_color = chess.WHITE
        self.selected_square = None
        self.last_move = None
        self.move_history = []
        self.captured = {chess.WHITE: [], chess.BLACK: []}
        self.pending_promotion = None
        self.time_minutes = time_minutes
        self.time_increment = time_increment
        self.player_time = time_minutes * 60.0
        self.opponent_time = time_minutes * 60.0
        self.last_tick = time.time()
        self.game_over = False
        self.result_message = ""
        self.resigned = False

    def reset(self, player_color=chess.WHITE, time_minutes=None, time_increment=None):
        self.board = chess.Board()
        self.player_color = player_color
        self.selected_square = None
        self.last_move = None
        self.move_history = []
        self.captured = {chess.WHITE: [], chess.BLACK: []}
        self.pending_promotion = None
        if time_minutes is not None:
            self.time_minutes = time_minutes
        if time_increment is not None:
            self.time_increment = time_increment
        self.player_time = self.time_minutes * 60.0
        self.opponent_time = self.time_minutes * 60.0
        self.last_tick = time.time()
        self.game_over = False
        self.result_message = ""
        self.resigned = False

    def get_legal_moves_for_square(self, square):
        if square is None:
            return None
        piece = self.board.piece_at(square)
        if piece is None:
            return None
        return [m for m in self.board.legal_moves if m.from_square == square]

    def try_select_square(self, square):
        if self.pending_promotion:
            return False
        return True

    def try_move(self, from_sq, to_sq):
        legal = self.get_legal_moves_for_square(from_sq)
        if not legal:
            return False

        matching = [m for m in legal if m.to_square == to_sq]
        if not matching:
            return False

        promotion_moves = [m for m in matching if m.promotion]
        if promotion_moves:
            self.pending_promotion = {
                "moves": promotion_moves,
                "from_sq": from_sq,
                "to_sq": to_sq,
            }
            return True

        self._execute_move(matching[0])
        return True

    def choose_promotion(self, piece_type):
        if not self.pending_promotion:
            return

        for move in self.pending_promotion["moves"]:
            if move.promotion == piece_type:
                self._execute_move(move)
                break

        self.pending_promotion = None

    def _execute_move(self, move):
        captured = self.board.piece_at(move.to_square)
        ep_captured = None

        if not captured and self.board.is_en_passant(move):
            ep_sq = chess.square(
                chess.square_file(move.to_square),
                chess.square_rank(move.from_square)
            )
            ep_captured = self.board.piece_at(ep_sq)

        san = self.board.san(move)
        self.board.push(move)
        self.move_history.append(san)
        self.last_move = move
        self.selected_square = None
        self.move_start_time = time.time()

        if captured:
            self.captured[
                chess.WHITE if captured.color == chess.BLACK else chess.BLACK
            ].append(captured)
        elif ep_captured:
            self.captured[
                chess.WHITE if ep_captured.color == chess.BLACK else chess.BLACK
            ].append(ep_captured)

        mover = chess.BLACK if self.board.turn else chess.WHITE
        if mover == self.player_color:
            self.player_time += self.time_increment
        else:
            self.opponent_time += self.time_increment

    def update_clocks(self):
        if self.game_over or self.pending_promotion:
            self.last_tick = time.time()
            return

        now = time.time()
        dt = now - self.last_tick
        self.last_tick = now

        if self.board.turn == self.player_color:
            self.player_time -= dt
        else:
            self.opponent_time -= dt

        if self.player_time <= 0:
            self.game_over = True
            self.result_message = "You lost on time!"
        elif self.opponent_time <= 0:
            self.game_over = True
            self.result_message = "Opponent lost on time!"

        self.player_time = max(0, self.player_time)
        self.opponent_time = max(0, self.opponent_time)

    def resign(self):
        self.game_over = True
        self.resigned = True
        winner = "Black" if self.player_color == chess.WHITE else "White"
        self.result_message = f"You resigned. {winner} wins."

    def is_game_over(self):
        if self.game_over:
            return True
        if self.board.is_game_over():
            self.game_over = True
            self.result_message = self._get_board_result()
            return True
        return False

    def _get_board_result(self):
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn else "White"
            return f"Checkmate! {winner} wins."
        elif self.board.is_stalemate():
            return "Draw by stalemate."
        elif self.board.is_insufficient_material():
            return "Draw by insufficient material."
        elif self.board.is_fifty_moves():
            return "Draw by fifty-move rule."
        elif self.board.is_repetition():
            return "Draw by threefold repetition."
        return "Game over."

    def game_result(self):
        return self.result_message

    def get_pgn(self):
        game = chess.pgn.Game.from_board(self.board)
        game.headers["Event"] = "VECTOR Game"
        exporter = chess.pgn.StringExporter(headers=True, variations=False,
                                            comments=False)
        return game.accept(exporter)
