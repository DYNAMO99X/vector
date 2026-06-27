import chess
import pygame
import constants
from pieces import load_pieces, get_piece_surface


class Board:
    def __init__(self, square_size=constants.SQUARE_SIZE, piece_style=0):
        self.square_size = square_size
        self.piece_style = piece_style
        self.pieces = load_pieces(piece_style, square_size)
        self.flipped = False

    def set_piece_style(self, style_id):
        self.piece_style = style_id
        self.pieces = load_pieces(style_id, self.square_size)

    def get_square_coords(self, square):
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)

        if self.flipped:
            col = 7 - file_idx
            row = 7 - rank_idx
        else:
            col = file_idx
            row = 7 - rank_idx

        x = constants.MARGIN_LEFT + col * self.square_size
        y = constants.MARGIN_TOP + row * self.square_size
        return x, y

    def get_square_at_pos(self, pos):
        mx, my = pos
        col = (mx - constants.MARGIN_LEFT) // self.square_size
        row = (my - constants.MARGIN_TOP) // self.square_size

        if col < 0 or col > 7 or row < 0 or row > 7:
            return None

        if self.flipped:
            file_idx = 7 - col
            rank_idx = 7 - row
        else:
            file_idx = col
            rank_idx = 7 - row

        if rank_idx < 0 or rank_idx > 7 or file_idx < 0 or file_idx > 7:
            return None

        return chess.square(file_idx, rank_idx)

    def draw(self, screen, board_state, selected_square=None,
             legal_moves=None, last_move=None, check_square=None, theme_colors=None,
             anim_data=None):
        self._draw_squares(screen, selected_square, last_move, check_square, theme_colors)
        self._draw_coordinates(screen, theme_colors)
        self._draw_legal_moves(screen, board_state, legal_moves)
        self._draw_pieces(screen, board_state)
        if anim_data and anim_data.get("active"):
            self._draw_animation(screen, board_state, anim_data)

    def _draw_squares(self, screen, selected_square, last_move, check_square, theme_colors=None):
        if theme_colors:
            light = theme_colors["light"]
            dark = theme_colors["dark"]
            last = theme_colors["last_move"]
            selected = theme_colors["selected"]
            check = theme_colors["check"]
        else:
            light = constants.LIGHT_SQUARE
            dark = constants.DARK_SQUARE
            last = constants.LAST_MOVE_SQUARE
            selected = constants.SELECTED_SQUARE
            check = constants.CHECK_SQUARE

        for rank in range(8):
            for file in range(8):
                if self.flipped:
                    sq = chess.square(7 - file, 7 - rank)
                else:
                    sq = chess.square(file, 7 - rank)

                is_light = (rank + file) % 2 == 0
                color = light if is_light else dark

                if last_move and sq in (last_move.from_square, last_move.to_square):
                    color = last

                if selected_square is not None and sq == selected_square:
                    color = selected

                if check_square is not None and sq == check_square:
                    color = check

                x = constants.MARGIN_LEFT + file * self.square_size
                y = constants.MARGIN_TOP + rank * self.square_size
                pygame.draw.rect(screen, color,
                                 (x, y, self.square_size, self.square_size))

    def _draw_coordinates(self, screen, theme_colors=None):
        if theme_colors:
            dark = theme_colors["dark"]
            light = theme_colors["light"]
        else:
            dark = constants.DARK_SQUARE
            light = constants.LIGHT_SQUARE

        font = pygame.font.SysFont("Segoe UI", 14, bold=True)

        for col in range(8):
            sq = chess.square(col, 0) if not self.flipped else chess.square(7 - col, 7)
            is_light = (chess.square_rank(sq) + chess.square_file(sq)) % 2 == 0
            color = dark if is_light else light
            f = "abcdefgh"[col] if not self.flipped else "hgfedcba"[col]
            text = font.render(f, True, color)
            x = constants.MARGIN_LEFT + col * self.square_size + self.square_size - 12
            y = constants.MARGIN_TOP + 7 * self.square_size + self.square_size - 16
            screen.blit(text, (x, y))

        for row in range(8):
            sq = chess.square(0, 7 - row) if not self.flipped else chess.square(7, row)
            is_light = (chess.square_rank(sq) + chess.square_file(sq)) % 2 == 0
            color = dark if is_light else light
            r = "87654321"[row] if not self.flipped else "12345678"[row]
            text = font.render(r, True, color)
            x = constants.MARGIN_LEFT + 4
            y = constants.MARGIN_TOP + row * self.square_size + 2
            screen.blit(text, (x, y))

    def _draw_legal_moves(self, screen, board_state, legal_moves):
        if not legal_moves:
            return

        captured_squares = set()
        for move in legal_moves:
            target_piece = board_state.piece_at(move.to_square)
            if target_piece is not None or board_state.is_en_passant(move):
                captured_squares.add(move.to_square)

        seen_targets = {}
        for move in legal_moves:
            if move.to_square not in seen_targets:
                seen_targets[move.to_square] = move

        for target_square, move in seen_targets.items():
            is_capture = target_square in captured_squares
            x, y = self.get_square_coords(target_square)

            overlay = pygame.Surface(
                (self.square_size, self.square_size), pygame.SRCALPHA
            )
            center = (self.square_size // 2, self.square_size // 2)
            radius = self.square_size // 6

            if is_capture:
                pygame.draw.circle(overlay, (0, 0, 0, 0), center, 0)
                pygame.draw.circle(overlay, (0, 0, 0, 80), center,
                                   self.square_size // 2 - 4, 5)
            else:
                pygame.draw.circle(overlay, (0, 0, 0, 80), center, radius)

            screen.blit(overlay, (x, y))

    def _draw_pieces(self, screen, board_state):
        for square in chess.SQUARES:
            piece = board_state.piece_at(square)
            if piece:
                surface = get_piece_surface(self.pieces, piece)
                if surface:
                    x, y = self.get_square_coords(square)
                    screen.blit(surface, (x, y))

    def _draw_animation(self, screen, board_state, anim_data):
        from_sq = anim_data["from_sq"]
        to_sq = anim_data["to_sq"]
        progress = anim_data["progress"]
        from_x, from_y = self.get_square_coords(from_sq)
        to_x, to_y = self.get_square_coords(to_sq)
        x = from_x + (to_x - from_x) * progress
        y = from_y + (to_y - from_y) * progress

        piece = board_state.piece_at(from_sq)
        if piece:
            surface = get_piece_surface(self.pieces, piece)
            if surface:
                screen.blit(surface, (x, y))

        extra = anim_data.get("extra") or {}
        if extra.get("rook_from") is not None:
            rfx, rfy = self.get_square_coords(extra["rook_from"])
            rtx, rty = self.get_square_coords(extra["rook_to"])
            rx = rfx + (rtx - rfx) * progress
            ry = rfy + (rty - rfy) * progress
            rook = board_state.piece_at(extra["rook_from"])
            if rook:
                rsurf = get_piece_surface(self.pieces, rook)
                if rsurf:
                    screen.blit(rsurf, (rx, ry))

        if extra.get("captured_sq") is not None:
            csq = extra["captured_sq"]
            cx, cy = self.get_square_coords(csq)
            cpiece = board_state.piece_at(csq)
            if cpiece:
                csurf = get_piece_surface(self.pieces, cpiece)
                if csurf:
                    fade = csurf.copy()
                    alpha = max(0, int(255 * (1.0 - progress)))
                    fade.set_alpha(alpha)
                    screen.blit(fade, (cx, cy))

    def flip(self):
        self.flipped = not self.flipped
