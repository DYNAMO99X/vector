import io
import os
import chess
import pygame
import constants


_piece_cache = {}


def _load_unicode_pieces(square_size):
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

    return pieces


def _get_style_dir(style_id):
    if style_id < 1 or style_id >= len(constants.PIECE_STYLES):
        return None
    _, dir_name, _, _ = constants.PIECE_STYLES[style_id]
    if dir_name is None:
        return None
    return os.path.join(constants.ASSETS_DIR, "pieces", dir_name)


def _crop_svg(surf):
    w, h = surf.get_size()
    min_x, min_y = w, h
    max_x, max_y = 0, 0
    for x in range(w):
        for y in range(h):
            if surf.get_at((x, y))[3] > 0:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + 1)
                max_y = max(max_y, y + 1)
    if min_x >= w:
        return surf
    margin = 2
    min_x = max(0, min_x - margin)
    min_y = max(0, min_y - margin)
    max_x = min(w, max_x + margin)
    max_y = min(h, max_y + margin)
    return surf.subsurface((min_x, min_y, max_x - min_x, max_y - min_y))


def _load_svg_pieces(style_id, square_size):
    pieces = None
    style_dir = _get_style_dir(style_id)
    if style_dir and os.path.isdir(style_dir):
        pieces = {}
        _, _, _, fit = constants.PIECE_STYLES[style_id]
        for color in ("w", "b"):
            for piece_type in ("K", "Q", "R", "B", "N", "P"):
                cache_id = f"{color}{piece_type}"
                svg_path = os.path.join(style_dir, f"{cache_id}.svg")
                if os.path.exists(svg_path):
                    try:
                        svg_data = open(svg_path, 'rb').read()
                        svg_text = svg_data.decode('utf-8')
                        if 'width=' not in svg_text[:300]:
                            svg_text = svg_text.replace('<svg ', '<svg width="200" height="200" ')
                        surf = pygame.image.load(io.BytesIO(svg_text.encode('utf-8')))
                        cropped = _crop_svg(surf)
                        cw, ch = cropped.get_size()
                        target = int(square_size * fit)
                        scale = min(target / cw, target / ch)
                        new_w = max(1, int(cw * scale))
                        new_h = max(1, int(ch * scale))
                        scaled = pygame.transform.smoothscale(
                            cropped, (new_w, new_h)
                        )
                        final = pygame.Surface(
                            (square_size, square_size), pygame.SRCALPHA
                        )
                        final.fill((0, 0, 0, 0))
                        x = (square_size - new_w) // 2
                        y = (square_size - new_h) // 2
                        final.blit(scaled, (x, y))
                        pieces[cache_id] = final
                    except Exception as e:
                        pieces[cache_id] = None
                else:
                    pieces[cache_id] = None
    return pieces


def load_pieces(style_id, square_size):
    cache_key = (style_id, square_size)
    if cache_key in _piece_cache:
        return _piece_cache[cache_key]

    if style_id == 0:
        pieces = _load_unicode_pieces(square_size)
    else:
        pieces = _load_svg_pieces(style_id, square_size)
        if pieces is None:
            pieces = _load_unicode_pieces(square_size)
        else:
            unicode_fallback = _load_unicode_pieces(square_size)
            for key, surf in pieces.items():
                if surf is None:
                    pieces[key] = unicode_fallback.get(key)

    _piece_cache[cache_key] = pieces
    return pieces


def get_piece_surface(pieces, piece):
    color_prefix = "w" if piece.color == chess.WHITE else "b"
    piece_letter = piece.symbol().upper()
    key = f"{color_prefix}{piece_letter}"
    return pieces.get(key)
