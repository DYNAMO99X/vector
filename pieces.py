import chess
import pygame
import constants


_piece_cache = {}


def load_pieces(square_size):
    if square_size in _piece_cache:
        return _piece_cache[square_size]

    pieces = {}
    font_size = int(square_size * 0.8)

    try:
        font = pygame.font.SysFont("segoeuisymbol", font_size, bold=False)
        test = font.render("X", True, (0, 0, 0))
    except Exception:
        try:
            font = pygame.font.SysFont("segoeui", font_size, bold=False)
        except Exception:
            font = pygame.font.Font(None, font_size)

    for color in ("w", "b"):
        for piece_type in ("K", "Q", "R", "B", "N", "P"):
            cache_id = f"{color}{piece_type}"
            unicode_char = constants.UNICODE_PIECES[cache_id]
            text_color = (240, 240, 240) if color == "w" else (40, 40, 40)
            outline = (0, 0, 0) if color == "w" else (200, 200, 200)

            text = font.render(unicode_char, True, text_color)
            outline_surf = font.render(unicode_char, True, outline)

            outline_size = max(2, square_size // 40)
            total_size = square_size
            surf = pygame.Surface((total_size, total_size), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))

            text_rect = text.get_rect(
                center=(total_size // 2, total_size // 2 + square_size // 20)
            )

            for dx in range(-outline_size, outline_size + 1):
                for dy in range(-outline_size, outline_size + 1):
                    if dx != 0 or dy != 0:
                        surf.blit(outline_surf,
                                  (text_rect.x + dx, text_rect.y + dy))

            surf.blit(text, text_rect)

            pieces[cache_id] = surf

    _piece_cache[square_size] = pieces
    return pieces


def get_piece_surface(pieces, piece):
    color_prefix = "w" if piece.color == chess.WHITE else "b"
    piece_letter = piece.symbol().upper()
    key = f"{color_prefix}{piece_letter}"
    return pieces.get(key)
