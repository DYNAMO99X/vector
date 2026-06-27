import sys
import os
import time
import threading
import urllib.request
import zipfile
import tempfile
import pygame
import chess
import constants
from board import Board
from game import Game, PIECE_VALUES
from settings import (
    GameSettings, draw_main_menu, draw_settings_list,
    draw_time_selector, handle_time_click,
    draw_bot_version_selector, draw_bot_depth_selector,
    handle_bot_version_click, handle_bot_depth_click,
    draw_book_selector, handle_book_click, handle_book_scroll,
    draw_board_theme_selector, handle_board_theme_click,
    draw_piece_style_selector, handle_piece_style_click,
    OPENING_BOOKS, BOOKS_DIR, BOT_VERSIONS,
)
from bot.engine import Engine

PROMOTION_PIECES = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]

MAIN_MENU = 0


def _do_bot_move(game, engine):
    move = engine.find_move(game.board)
    if move:
        game._execute_move(move)
COLOR_CHOICE = 1
SETTINGS_LIST = 2
TIME_SELECTOR = 3
PLAYING = 4
MODE_SELECT = 5
BOT_VERSION_SELECTOR = 6
BOT_DEPTH_SELECTOR = 7
SELF_PLAY_CONFIG = 8
BOOK_SELECTOR = 9
BOARD_THEME_SELECTOR = 10
PIECE_STYLE_SELECTOR = 11

# Book download state
_book_download_progress = {}
_book_download_idx = None
_book_download_active = False
_book_pending_dl = None


def _book_download_worker(idx, filename, url, is_archive):
    global _book_download_progress, _book_download_idx, _book_download_active
    _book_download_progress[idx] = 0
    _book_download_idx = idx
    _book_download_active = True

    def reporthook(blocknum, blocksize, totalsize):
        if totalsize > 0:
            pct = min(99, int(blocknum * blocksize * 100 / totalsize))
            _book_download_progress[idx] = pct

    try:
        tmp = os.path.join(tempfile.gettempdir(), f"vector_book_{filename}")
        if url.endswith(".7z"):
            tmp += ".7z"
        else:
            tmp += ".zip"
        urllib.request.urlretrieve(url, tmp, reporthook)

        _book_download_progress[idx] = -1  # extracting
        dest = os.path.join(BOOKS_DIR, filename)
        os.makedirs(BOOKS_DIR, exist_ok=True)

        if url.endswith(".7z"):
            import py7zr
            import glob as _glob
            with py7zr.SevenZipFile(tmp, 'r') as z:
                z.extractall(path=BOOKS_DIR)
            # handle case where 7z internal filename differs from expected
            if not os.path.exists(dest):
                bins = _glob.glob(os.path.join(BOOKS_DIR, "*.bin"))
                if bins:
                    os.rename(bins[0], dest)
        else:
            with zipfile.ZipFile(tmp, 'r') as z:
                z.extract(filename, path=BOOKS_DIR)

        os.remove(tmp)
        _book_download_progress[idx] = 100
    except Exception:
        _book_download_progress[idx] = -2  # error
    finally:
        _book_download_active = False


def _get_book_path(settings):
    return os.path.join(BOOKS_DIR, settings.book_filename) if settings.book_enabled else None


def draw_panel(screen, game, board_view, scroll_offset, self_play=False):
    panel_rect = pygame.Rect(constants.PANEL_X, constants.MARGIN_TOP,
                             constants.PANEL_WIDTH, constants.BOARD_SIZE)
    pygame.draw.rect(screen, constants.THEME["panel_bg"], panel_rect)
    pygame.draw.rect(screen, constants.THEME["panel_border"], panel_rect, 2)

    font = pygame.font.SysFont("Segoe UI", 18, bold=True)
    font_big = pygame.font.SysFont("Segoe UI", 16)
    font_small = pygame.font.SysFont("Segoe UI", 13)
    font_header = pygame.font.SysFont("Segoe UI", 22, bold=True)

    x = panel_rect.x + 15
    w = panel_rect.width - 30

    title = font_header.render("VECTOR", True, constants.THEME["text_title"])
    screen.blit(title, (x, panel_rect.y + 10))

    subtitle = font_small.render("Vibe-Engineered Chess", True, constants.THEME["text_dim"])
    screen.blit(subtitle, (x, panel_rect.y + 38))

    top = panel_rect.y + 68

    turn_text = font.render(
        f"Turn: {'White' if game.board.turn == chess.WHITE else 'Black'}",
        True, constants.THEME["text"]
    )
    screen.blit(turn_text, (x, top))

    clock_y = top + 32
    w_time = game.player_time if game.player_color == chess.WHITE else game.opponent_time
    b_time = game.opponent_time if game.player_color == chess.WHITE else game.player_time
    if self_play:
        w_label = "White"
        b_label = "Black"
    else:
        w_label = "You" if game.player_color == chess.WHITE else "Opp"
        b_label = "Opp" if game.player_color == chess.WHITE else "You"

    w_min, w_sec = divmod(int(w_time), 60)
    b_min, b_sec = divmod(int(b_time), 60)
    w_str = f"{w_label}: {w_min:02d}:{w_sec:02d}"
    b_str = f"{b_label}: {b_min:02d}:{b_sec:02d}"

    is_w_turn = game.board.turn == chess.WHITE
    accent_color = (255, 255, 200)
    w_color = accent_color if is_w_turn else constants.THEME["text"]
    b_color = accent_color if not is_w_turn else constants.THEME["text"]

    wc = font_big.render(w_str, True, w_color)
    screen.blit(wc, (x + 30, clock_y))
    bc = font_big.render(b_str, True, b_color)
    screen.blit(bc, (x + 30, clock_y + 22))

    pip_font = pygame.font.SysFont("Segoe UI Symbol", 14)
    wpip = pip_font.render("\u25CF", True, (240, 240, 240))
    screen.blit(wpip, (x, clock_y))
    bpip = pip_font.render("\u25CF", True, constants.THEME["text"])
    screen.blit(bpip, (x, clock_y + 22))

    cap_y = clock_y + 50
    cap_label = font_small.render("Captured", True, constants.THEME["text_dim"])
    screen.blit(cap_label, (x, cap_y))
    cap_y += 20

    for color_name, cap_list, prefix in [
        ("by White: ", game.captured[chess.BLACK], "b"),
        ("by Black: ", game.captured[chess.WHITE], "w"),
    ]:
        if not cap_list:
            continue
        sorted_caps = sorted(
            cap_list,
            key=lambda p: PIECE_VALUES.get(p.piece_type, 0),
            reverse=True
        )
        line = font_small.render(color_name, True, constants.THEME["text_dim"])
        screen.blit(line, (x, cap_y))
        cap_y += 16
        cap_chars = [
            constants.UNICODE_PIECES.get(f"{prefix}{p.symbol().upper()}", "?")
            for p in sorted_caps
        ]
        piece_font = pygame.font.SysFont("Segoe UI Symbol", 16)
        for start in range(0, len(cap_chars), 8):
            chunk = "".join(cap_chars[start:start + 8])
            r = piece_font.render(chunk, True, constants.THEME["text"])
            screen.blit(r, (x + 5, cap_y))
            cap_y += 20

    moves_label = font.render("Moves", True, constants.THEME["text"])
    moves_y = max(cap_y + 10, panel_rect.y + 300)
    screen.blit(moves_label, (x, moves_y))
    moves_y += 30

    move_area_height = panel_rect.bottom - moves_y - 50
    area_rect = pygame.Rect(x - 5, moves_y - 5, w + 10, move_area_height + 10)
    pygame.draw.rect(screen, constants.THEME["move_well_bg"], area_rect, border_radius=4)

    old_clip = screen.get_clip()
    screen.set_clip(area_rect)

    line_height = 20
    max_visible = move_area_height // line_height
    total_moves = len(game.move_history)
    max_offset = max(0, total_moves - max_visible)
    scroll_offset = max(0, min(scroll_offset, max_offset))

    start_idx = scroll_offset
    if total_moves > 0 and start_idx % 2 == 1:
        start_idx = max(0, start_idx - 1)

    display_y = moves_y
    i = start_idx
    while i < total_moves and display_y + line_height <= moves_y + move_area_height:
        if i % 2 == 0:
            num = i // 2 + 1
            num_text = font_small.render(f"{num}.", True, constants.THEME["text_dim"])
            screen.blit(num_text, (x, display_y))
            offset = 28
        else:
            offset = 75

        san_color = constants.THEME["text"] if i % 2 == 0 else constants.THEME["text_dim"]
        san_text = font_small.render(game.move_history[i], True, san_color)
        screen.blit(san_text, (x + offset, display_y))

        if i % 2 == 1:
            display_y += line_height
        i += 1

    screen.set_clip(old_clip)

    if total_moves > max_visible:
        scrollbar_y = area_rect.y
        track_h = area_rect.h
        thumb_h = max(20, track_h * max_visible // max(1, total_moves))
        avail = track_h - thumb_h
        thumb_pos = scrollbar_y + avail * scroll_offset // max(1, max_offset)

        pygame.draw.rect(screen, constants.THEME["scroll_bg"],
                         (x + w - 8, scrollbar_y, 6, track_h),
                         border_radius=3)
        pygame.draw.rect(screen, constants.THEME["scroll_thumb"],
                         (x + w - 8, thumb_pos, 6, thumb_h),
                         border_radius=3)

    btn_y = panel_rect.bottom - 36
    resign_rect = pygame.Rect(x, btn_y, 80, 28)
    pygame.draw.rect(screen, constants.THEME["btn_danger_fill"], resign_rect, border_radius=4)
    pygame.draw.rect(screen, constants.THEME["btn_danger_border"], resign_rect, 1, border_radius=4)
    resign_text = font_small.render("Resign", True, constants.THEME["btn_danger_text"])
    rt_rect = resign_text.get_rect(center=resign_rect.center)
    screen.blit(resign_text, rt_rect)

    return resign_rect, scroll_offset


def draw_promotion_dialog(screen, game):
    overlay = pygame.Surface((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
    overlay.set_alpha(160)
    overlay.fill(constants.THEME["overlay"])
    screen.blit(overlay, (0, 0))

    dialog_w = 360
    dialog_h = 120
    dialog_x = (constants.WINDOW_WIDTH - dialog_w) // 2
    dialog_y = (constants.WINDOW_HEIGHT - dialog_h) // 2

    pygame.draw.rect(screen, constants.THEME["btn_inactive_fill"],
                     (dialog_x, dialog_y, dialog_w, dialog_h),
                     border_radius=8)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"],
                     (dialog_x, dialog_y, dialog_w, dialog_h), 2,
                     border_radius=8)

    font = pygame.font.SysFont("Segoe UI", 16, bold=True)
    prompt = font.render("Choose promotion piece:", True, constants.THEME["text"])
    pr = prompt.get_rect(center=(constants.WINDOW_WIDTH // 2, dialog_y + 25))
    screen.blit(prompt, pr)

    color_prefix = "w" if game.board.turn == chess.WHITE else "b"
    button_size = 60
    gap = 20
    total_w = button_size * 4 + gap * 3
    start_x = dialog_x + (dialog_w - total_w) // 2
    button_y = dialog_y + 45

    buttons = []
    for i, piece_type in enumerate(PROMOTION_PIECES):
        piece_key = f"{color_prefix}{piece_type.symbol()}"
        bx = start_x + i * (button_size + gap)
        by = button_y
        rect = pygame.Rect(bx, by, button_size, button_size)
        pygame.draw.rect(screen, constants.THEME["btn_row_fill"], rect, border_radius=6)
        pygame.draw.rect(screen, constants.THEME["btn_inactive_border"], rect, 1, border_radius=6)

        pf = pygame.font.SysFont("Segoe UI Symbol", 40)
        unicode_char = constants.UNICODE_PIECES[piece_key]
        text = pf.render(unicode_char, True, constants.THEME["text_bright"])
        outline = pf.render(unicode_char, True, constants.THEME["overlay"])

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    screen.blit(outline,
                                (bx + 30 - outline.get_width() // 2 + dx,
                                 by + 30 - outline.get_height() // 2 + dy))
        screen.blit(text, (bx + 30 - text.get_width() // 2,
                           by + 30 - text.get_height() // 2))
        buttons.append((rect, piece_type))

    hint = pygame.font.SysFont("Segoe UI", 12).render(
        "Keys: Q R B N", True, constants.THEME["text_dim"]
    )
    hr = hint.get_rect(center=(constants.WINDOW_WIDTH // 2, dialog_y + dialog_h - 10))
    screen.blit(hint, hr)

    return buttons


def draw_mode_select(screen, settings):
    screen.fill(constants.THEME["bg"])

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    title = font_big.render("Select Game Mode", True, constants.THEME["text_title"])
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 110))
    screen.blit(title, tr)

    button_w = 300
    button_h = 70
    btn_x = constants.WINDOW_WIDTH // 2 - button_w // 2

    bot_rect = pygame.Rect(btn_x, 170, button_w, button_h)
    pygame.draw.rect(screen, constants.THEME["btn_accent_fill"], bot_rect, border_radius=12)
    pygame.draw.rect(screen, constants.THEME["btn_accent_border"], bot_rect, 2, border_radius=12)

    bot_title = font_mid.render(
        f"vs VECTOR {BOT_VERSIONS[settings.bot_version][0]}", True, constants.THEME["btn_accent_text"]
    )
    bt_rect = bot_title.get_rect(center=(bot_rect.centerx, bot_rect.centery - 10))
    screen.blit(bot_title, bt_rect)

    bot_sub = font_small.render("Play against the engine", True, constants.THEME["text_dim"])
    bs_rect = bot_sub.get_rect(center=(bot_rect.centerx, bot_rect.centery + 14))
    screen.blit(bot_sub, bs_rect)

    self_play_rect = pygame.Rect(btn_x, 260, button_w, button_h)
    self_play_fill = (55, 65, 80) if constants.THEME is constants.DARK else (200, 205, 215)
    self_play_border = (130, 185, 220) if constants.THEME is constants.DARK else (90, 140, 180)
    self_play_title_color = (180, 220, 245) if constants.THEME is constants.DARK else (30, 60, 90)
    self_play_sub_color = (160, 185, 205) if constants.THEME is constants.DARK else (80, 100, 120)
    pygame.draw.rect(screen, self_play_fill, self_play_rect, border_radius=12)
    pygame.draw.rect(screen, self_play_border, self_play_rect, 2, border_radius=12)

    sp_title = font_mid.render("Self-Play", True, self_play_title_color)
    st_rect = sp_title.get_rect(center=(self_play_rect.centerx, self_play_rect.centery - 10))
    screen.blit(sp_title, st_rect)

    sp_sub = font_small.render("Watch VECTOR play itself", True, self_play_sub_color)
    ss_rect = sp_sub.get_rect(center=(self_play_rect.centerx, self_play_rect.centery + 14))
    screen.blit(sp_sub, ss_rect)

    player_rect = pygame.Rect(btn_x, 350, button_w, button_h)
    pygame.draw.rect(screen, constants.THEME["btn_inactive_fill"], player_rect, border_radius=12)
    pygame.draw.rect(screen, constants.THEME["btn_inactive_border"], player_rect, 2, border_radius=12)

    pl_title = font_mid.render("vs Player", True, constants.THEME["btn_inactive_text"])
    pt_rect = pl_title.get_rect(center=(player_rect.centerx, player_rect.centery - 10))
    screen.blit(pl_title, pt_rect)

    pl_sub = font_small.render("Play against a friend locally", True, constants.THEME["btn_inactive_text_dim"])
    ps_rect = pl_sub.get_rect(center=(player_rect.centerx, player_rect.centery + 14))
    screen.blit(pl_sub, ps_rect)

    back_rect = pygame.Rect(constants.WINDOW_WIDTH // 2 - 50, 460, 100, 36)
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], back_rect, border_radius=6)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], back_rect, 1, border_radius=6)
    back_text = font_small.render("< Back", True, constants.THEME["btn_back_text"])
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return bot_rect, self_play_rect, player_rect, back_rect


def draw_color_choice(screen):
    screen.fill(constants.THEME["bg"])

    font = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 16)

    title = font.render("VECTOR", True, constants.THEME["text_bright"])
    title_rect = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 160))
    screen.blit(title, title_rect)

    subtitle = font_small.render(
        "Vibe-Engineered Chess Tactician for Online Rankings",
        True, constants.THEME["text_dim"]
    )
    sub_rect = subtitle.get_rect(center=(constants.WINDOW_WIDTH // 2, 195))
    screen.blit(subtitle, sub_rect)

    prompt_font = pygame.font.SysFont("Segoe UI", 22)
    prompt = prompt_font.render("Choose your color:", True, constants.THEME["text"])
    prompt_rect = prompt.get_rect(center=(constants.WINDOW_WIDTH // 2, 290))
    screen.blit(prompt, prompt_rect)

    white_rect = pygame.Rect(0, 0, 200, 55)
    white_rect.center = (constants.WINDOW_WIDTH // 2 - 120, 370)
    pygame.draw.rect(screen, constants.THEME["btn_inactive_fill"], white_rect, border_radius=8)
    pygame.draw.rect(screen, (200, 200, 200), white_rect, 2, border_radius=8)
    w_text = font_small.render("Play as White", True, constants.THEME["btn_inactive_text"])
    w_rect = w_text.get_rect(center=white_rect.center)
    screen.blit(w_text, w_rect)

    black_rect = pygame.Rect(0, 0, 200, 55)
    black_rect.center = (constants.WINDOW_WIDTH // 2 + 120, 370)
    pygame.draw.rect(screen, constants.THEME["btn_inactive_fill"], black_rect, border_radius=8)
    pygame.draw.rect(screen, constants.THEME["btn_inactive_border"], black_rect, 2, border_radius=8)
    b_text = font_small.render("Play as Black", True, constants.THEME["btn_inactive_text"])
    b_rect = b_text.get_rect(center=black_rect.center)
    screen.blit(b_text, b_rect)

    back_rect = pygame.Rect(constants.WINDOW_WIDTH // 2 - 50, 460, 100, 36)
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], back_rect, border_radius=6)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], back_rect, 1, border_radius=6)
    back_text = font_small.render("< Back", True, constants.THEME["btn_back_text"])
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return white_rect, black_rect, back_rect


SELF_PLAY_DELAYS = [0.1, 0.5, 1.0, 2.0]


def draw_self_play_config(screen, settings, white_ver, black_ver, delay):
    screen.fill(constants.THEME["bg"])

    font_big = pygame.font.SysFont("Segoe UI", 26, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 18, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 14)
    font_button = pygame.font.SysFont("Segoe UI", 15, bold=True)

    title = font_big.render("Self-Play Setup", True, constants.THEME["text_title"])
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 40))
    screen.blit(title, tr)

    sections = [
        ("White Engine", 80, white_ver, 0),
        ("Black Engine", 180, black_ver, 1),
    ]

    buttons = {"white": [], "black": [], "delay": [], "start": None, "back": None}
    btn_w = 130
    btn_h = 44
    gap = 10
    total_w = 4 * btn_w + 3 * gap
    start_x = constants.WINDOW_WIDTH // 2 - total_w // 2

    for label, y, current_ver, key in sections:
        lbl = font_mid.render(label, True, constants.THEME["text_bright"])
        screen.blit(lbl, (start_x, y))
        row_btns = []
        for vi, (vname, _) in enumerate(BOT_VERSIONS):
            bx = start_x + vi * (btn_w + gap)
            by = y + 28
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            is_active = vi == current_ver
            bg = constants.THEME["btn_accent_fill"] if is_active else constants.THEME["btn_inactive_fill"]
            border = constants.THEME["btn_accent_border"] if is_active else constants.THEME["btn_inactive_border"]
            pygame.draw.rect(screen, bg, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 2, border_radius=8)
            color = constants.THEME["btn_accent_text"] if is_active else constants.THEME["btn_inactive_text"]
            txt = font_button.render(f"Mark {vi + 1}", True, color)
            t_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, t_rect)
            row_btns.append((rect, vi))
        buttons["white" if key == 0 else "black"] = row_btns

    delay_y = 280
    delay_lbl = font_mid.render("Move Delay", True, constants.THEME["text_bright"])
    screen.blit(delay_lbl, (start_x, delay_y))

    delay_btns = []
    for di, d in enumerate(SELF_PLAY_DELAYS):
        bx = start_x + di * (btn_w + gap)
        by = delay_y + 28
        rect = pygame.Rect(bx, by, btn_w, btn_h)
        is_active = abs(d - delay) < 0.01
        bg = constants.THEME["btn_accent_fill"] if is_active else constants.THEME["btn_inactive_fill"]
        border = constants.THEME["btn_accent_border"] if is_active else constants.THEME["btn_inactive_border"]
        pygame.draw.rect(screen, bg, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 2, border_radius=8)
        label = f"{d:.1f}s" if d >= 1.0 else f"{d:.1f}s"
        color = constants.THEME["btn_accent_text"] if is_active else constants.THEME["btn_inactive_text"]
        txt = font_button.render(label, True, color)
        t_rect = txt.get_rect(center=rect.center)
        screen.blit(txt, t_rect)
        delay_btns.append((rect, d))
    buttons["delay"] = delay_btns

    btn_y = constants.WINDOW_HEIGHT - 70

    start_rect = pygame.Rect(constants.WINDOW_WIDTH // 2 - 110, btn_y, 100, 42)
    pygame.draw.rect(screen, constants.THEME["btn_accent_fill"], start_rect, border_radius=8)
    pygame.draw.rect(screen, constants.THEME["btn_accent_border"], start_rect, 2, border_radius=8)
    start_text = font_mid.render("Start", True, constants.THEME["btn_accent_text"])
    st_rect = start_text.get_rect(center=start_rect.center)
    screen.blit(start_text, st_rect)
    buttons["start"] = start_rect

    back_rect = pygame.Rect(constants.WINDOW_WIDTH // 2 + 20, btn_y, 100, 42)
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], back_rect, border_radius=8)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], back_rect, 2, border_radius=8)
    back_text = font_mid.render("Back", True, constants.THEME["btn_back_text"])
    btr = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, btr)
    buttons["back"] = back_rect

    return buttons


def handle_self_play_click(mx, my, buttons):
    for rect, vi in buttons["white"]:
        if rect.collidepoint(mx, my):
            return "white_ver", vi
    for rect, vi in buttons["black"]:
        if rect.collidepoint(mx, my):
            return "black_ver", vi
    for rect, d in buttons["delay"]:
        if rect.collidepoint(mx, my):
            return "delay", d
    if buttons["start"].collidepoint(mx, my):
        return "start", None
    if buttons["back"].collidepoint(mx, my):
        return "back", None
    return None, None


def _draw_hover_border(screen, rect):
    c = constants.THEME["btn_accent_border"]
    border_color = (min(255, c[0] + 50), min(255, c[1] + 50), min(255, c[2] + 50))
    br = min(12, rect.width // 5)
    pygame.draw.rect(screen, border_color, rect, 3, border_radius=br)


def _bot_search_worker(engine, board, max_time, result_out):
    try:
        move = engine.find_move(board, max_time=max_time)
        result_out.append(move)
    except Exception:
        result_out.append(None)


def main():
    global _book_pending_dl
    pygame.init()
    screen = pygame.display.set_mode(
        (constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)
    )
    pygame.display.set_caption(constants.SCREEN_TITLE)
    clock = pygame.time.Clock()

    settings = GameSettings()
    constants.set_theme(settings.theme)
    board_view = Board(piece_style=settings.piece_style)
    game = Game(settings.time_minutes, settings.time_increment)
    engine = Engine(depth=settings.bot_depth, version=settings.bot_version, book_enabled=settings.book_enabled, book_path=_get_book_path(settings))
    running = True
    state = MAIN_MENU
    vs_bot = False
    scroll_offset = 0
    promotion_buttons = None
    resign_rect = pygame.Rect(0, 0, 1, 1)
    game_over_pgn_copied = False
    bot_move_pending = False
    bot_ready_time = 0
    bot_delay = 2.0
    bot_pending_move = None
    bot_search_thread = None
    bot_search_running = False
    bot_search_result_container = None
    self_play = False
    engine_white = None
    engine_black = None
    self_play_white_ver = 3
    self_play_black_ver = 2
    self_play_delay = 0.5
    anim_active = False
    anim_move = None
    anim_start_time = 0.0
    anim_duration = 0.25
    anim_extra = {}
    fade_active = False
    fade_start = 0.0
    fade_duration = 0.15
    mouse_pos = None
    prev_state = None

    while running:
        dt = clock.tick(constants.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state == PLAYING:
                    anim_active = False
                    anim_move = None
                    if self_play:
                        if engine_white: engine_white._abort = True
                        if engine_black: engine_black._abort = True
                    else:
                        engine._abort = True
                    if bot_search_thread and bot_search_thread.is_alive():
                        bot_search_thread.join(timeout=0.5)
                    state = MAIN_MENU
                elif state in (MODE_SELECT, SETTINGS_LIST, SELF_PLAY_CONFIG):
                    state = MAIN_MENU
                elif state == BOOK_SELECTOR:
                    _book_pending_dl = None
                    state = SETTINGS_LIST
                elif state in (TIME_SELECTOR, BOT_VERSION_SELECTOR, BOT_DEPTH_SELECTOR,
                               BOARD_THEME_SELECTOR, PIECE_STYLE_SELECTOR):
                    state = SETTINGS_LIST
                elif state == COLOR_CHOICE:
                    state = MODE_SELECT
                elif state == MAIN_MENU:
                    running = False
                continue

            if state == MAIN_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    play_rect, settings_rect = draw_main_menu(screen)
                    if play_rect.collidepoint(mx, my):
                        state = MODE_SELECT
                    elif settings_rect.collidepoint(mx, my):
                        state = SETTINGS_LIST
                continue

            if state == MODE_SELECT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    bot_rect, self_play_rect, player_rect, back_rect = draw_mode_select(screen, settings)
                    if back_rect.collidepoint(mx, my):
                        state = MAIN_MENU
                    elif bot_rect.collidepoint(mx, my):
                        vs_bot = True
                        self_play = False
                        state = COLOR_CHOICE
                    elif self_play_rect.collidepoint(mx, my):
                        vs_bot = False
                        self_play = True
                        state = SELF_PLAY_CONFIG
                    elif player_rect.collidepoint(mx, my):
                        vs_bot = False
                        self_play = False
                        state = COLOR_CHOICE
                continue

            if state == SETTINGS_LIST:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    buttons, back_rect = draw_settings_list(screen, settings)
                    if back_rect.collidepoint(mx, my):
                        state = MAIN_MENU
                    for rect, label, enabled in buttons:
                        if enabled and rect.collidepoint(mx, my):
                            if label == "Match Time":
                                state = TIME_SELECTOR
                            elif label == "Bot Version":
                                state = BOT_VERSION_SELECTOR
                            elif label == "Bot Depth":
                                state = BOT_DEPTH_SELECTOR
                            elif label == "Piece Style":
                                state = PIECE_STYLE_SELECTOR
                            elif label == "Opening Book":
                                state = BOOK_SELECTOR
                            elif label == "Board Theme":
                                state = BOARD_THEME_SELECTOR
                            elif label == "Theme":
                                settings.theme = "light" if settings.theme == "dark" else "dark"
                                constants.set_theme(settings.theme)
                continue

            if state == TIME_SELECTOR:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    preset_buttons, mins_controls, inc_controls, save_rect, back_btn_rect = \
                        draw_time_selector(screen, settings)
                    if back_btn_rect.collidepoint(mx, my):
                        state = SETTINGS_LIST
                    else:
                        result = handle_time_click(
                            settings, mx, my, preset_buttons,
                            mins_controls, inc_controls, save_rect
                        )
                        if result == "save":
                            state = SETTINGS_LIST
                continue

            if state == BOT_VERSION_SELECTOR:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    version_buttons, back_rect = draw_bot_version_selector(screen, settings)
                    result = handle_bot_version_click(
                        settings, mx, my, version_buttons, back_rect
                    )
                    if result == "back":
                        state = SETTINGS_LIST
                    else:
                        engine.version = settings.bot_version
                continue

            if state == BOT_DEPTH_SELECTOR:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    preset_buttons, depth_controls, save_rect, back_btn_rect = \
                        draw_bot_depth_selector(screen, settings)
                    if back_btn_rect.collidepoint(mx, my):
                        state = SETTINGS_LIST
                    else:
                        result = handle_bot_depth_click(
                            settings, mx, my, preset_buttons,
                            depth_controls, save_rect
                        )
                        if result == "save":
                            engine.depth = settings.bot_depth
                            state = SETTINGS_LIST
                continue

            if state == SELF_PLAY_CONFIG:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    buttons = draw_self_play_config(screen, settings, self_play_white_ver, self_play_black_ver, self_play_delay)
                    result, value = handle_self_play_click(mx, my, buttons)
                    if result == "back":
                        state = MAIN_MENU
                    elif result == "start":
                        if engine:
                            engine._abort = True
                        engine_white = Engine(depth=settings.bot_depth, version=self_play_white_ver, book_enabled=settings.book_enabled, book_path=_get_book_path(settings))
                        engine_black = Engine(depth=settings.bot_depth, version=self_play_black_ver, book_enabled=settings.book_enabled, book_path=_get_book_path(settings))
                        game.reset(
                            player_color=chess.WHITE,
                            time_minutes=settings.time_minutes,
                            time_increment=settings.time_increment
                        )
                        board_view.set_piece_style(settings.piece_style)
                        board_view.flipped = False
                        state = PLAYING
                        scroll_offset = 0
                        promotion_buttons = None
                        game_over_pgn_copied = False
                        anim_active = False
                        anim_move = None
                        bot_move_pending = True
                        bot_pending_move = None
                    elif result == "white_ver":
                        self_play_white_ver = value
                    elif result == "black_ver":
                        self_play_black_ver = value
                    elif result == "delay":
                        self_play_delay = value
                continue

            if state == BOOK_SELECTOR:
                if event.type == pygame.MOUSEWHEEL:
                    handle_book_scroll(event.y)
                    _book_pending_dl = None
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in (4, 5):
                        continue
                    mx, my = event.pos
                    book_buttons, back_rect, dl_rect = draw_book_selector(screen, settings, pending_idx=_book_pending_dl)
                    result, value = handle_book_click(settings, mx, my, book_buttons, back_rect, dl_rect)
                    if result == "back":
                        _book_pending_dl = None
                        state = SETTINGS_LIST
                    elif result == "select":
                        engine.update_book_path(_get_book_path(settings))
                        _book_pending_dl = None
                        state = SETTINGS_LIST
                    elif result == "pending":
                        _book_pending_dl = value
                    elif result == "download_confirm" and _book_pending_dl is not None:
                        pfn = OPENING_BOOKS[_book_pending_dl][1]
                        purl = OPENING_BOOKS[_book_pending_dl][5]
                        parchive = OPENING_BOOKS[_book_pending_dl][6]
                        if not _book_download_active:
                            t = threading.Thread(
                                target=_book_download_worker,
                                args=(_book_pending_dl, pfn, purl, parchive),
                                daemon=True,
                            )
                            t.start()
                continue

            if state == BOARD_THEME_SELECTOR:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    theme_buttons, back_rect = draw_board_theme_selector(screen, settings)
                    result, value = handle_board_theme_click(settings, mx, my, theme_buttons, back_rect)
                    if result == "back":
                        state = SETTINGS_LIST
                    elif result == "select":
                        state = SETTINGS_LIST
                continue

            if state == PIECE_STYLE_SELECTOR:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    style_buttons, back_rect = draw_piece_style_selector(screen, settings)
                    result, value = handle_piece_style_click(settings, mx, my, style_buttons, back_rect)
                    if result == "back":
                        state = SETTINGS_LIST
                    elif result == "select":
                        state = SETTINGS_LIST
                continue

            if state == COLOR_CHOICE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    w_rect, b_rect, back_rect = draw_color_choice(screen)
                    if back_rect.collidepoint(mx, my):
                        state = MAIN_MENU
                    elif w_rect.collidepoint(mx, my):
                        game.reset(
                            player_color=chess.WHITE,
                            time_minutes=settings.time_minutes,
                            time_increment=settings.time_increment
                        )
                        board_view.set_piece_style(settings.piece_style)
                        board_view.flipped = False
                        state = PLAYING
                        scroll_offset = 0
                        promotion_buttons = None
                        game_over_pgn_copied = False
                        anim_active = False
                        anim_move = None
                        if vs_bot and game.board.turn != game.player_color:
                            bot_move_pending = True
                            bot_pending_move = None
                    elif b_rect.collidepoint(mx, my):
                        game.reset(
                            player_color=chess.BLACK,
                            time_minutes=settings.time_minutes,
                            time_increment=settings.time_increment
                        )
                        board_view.set_piece_style(settings.piece_style)
                        board_view.flipped = True
                        state = PLAYING
                        scroll_offset = 0
                        promotion_buttons = None
                        game_over_pgn_copied = False
                        anim_active = False
                        anim_move = None
                        if vs_bot and game.board.turn != game.player_color:
                            bot_move_pending = True
                            bot_pending_move = None
                continue

            if state == PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    settings.theme = "light" if settings.theme == "dark" else "dark"
                    constants.set_theme(settings.theme)
                    continue

                if anim_active or bot_move_pending or (vs_bot and not self_play and game.board.turn != game.player_color):
                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        board_view.flip()
                        continue
                    if event.key == pygame.K_n:
                        anim_active = False
                        anim_move = None
                        if self_play:
                            if engine_white: engine_white._abort = True
                            if engine_black: engine_black._abort = True
                        else:
                            engine._abort = True
                        if bot_search_thread and bot_search_thread.is_alive():
                            bot_search_thread.join(timeout=0.5)
                        state = MAIN_MENU
                        scroll_offset = 0
                        promotion_buttons = None
                        continue

                if game.pending_promotion:
                    if event.type == pygame.KEYDOWN:
                        key_map = {
                            pygame.K_q: chess.QUEEN,
                            pygame.K_r: chess.ROOK,
                            pygame.K_b: chess.BISHOP,
                            pygame.K_n: chess.KNIGHT,
                        }
                        if event.key in key_map:
                            promo_move = game.choose_promotion(key_map[event.key])
                            if promo_move is not None:
                                promotion_buttons = None
                                anim_active = True
                                anim_move = promo_move
                                anim_start_time = time.time()
                                anim_duration = 0.25
                                anim_extra = {}
                            continue
                    if event.type == pygame.MOUSEBUTTONDOWN and promotion_buttons:
                        mx, my = event.pos
                        for rect, piece_type in promotion_buttons:
                            if rect.collidepoint(mx, my):
                                promo_move = game.choose_promotion(piece_type)
                                if promo_move is not None:
                                    promotion_buttons = None
                                    anim_active = True
                                    anim_move = promo_move
                                    anim_start_time = time.time()
                                    anim_duration = 0.25
                                    anim_extra = {}
                        continue
                    continue

                is_game_over = game.is_game_over() or game.resigned

                if is_game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        pgn_btn_rect = pygame.Rect(0, 0, 120, 32)
                        pgn_btn_rect.center = (
                            constants.WINDOW_WIDTH // 2,
                            constants.WINDOW_HEIGHT // 2 + 50
                        )
                        if pgn_btn_rect.collidepoint(mx, my):
                            pgn = game.get_pgn()
                            try:
                                pygame.scrap.init()
                                pygame.scrap.put(pygame.SCRAP_TEXT, pgn.encode("utf-8"))
                            except Exception:
                                pass
                            game_over_pgn_copied = True
                    continue

                if event.type == pygame.MOUSEWHEEL:
                    scroll_offset -= event.y * 3
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    if resign_rect.collidepoint(mx, my):
                        game.resign()
                        continue

                    square = board_view.get_square_at_pos((mx, my))
                    if square is None:
                        continue

                    piece = game.board.piece_at(square)

                    if piece and piece.color == game.board.turn:
                        game.selected_square = square
                    elif game.selected_square is not None:
                        move = game.validate_move(game.selected_square, square)
                        if move is not None:
                            extra = {}
                            piece = game.board.piece_at(move.from_square)
                            if piece and piece.piece_type == chess.KING \
                                    and abs(move.to_square - move.from_square) == 2:
                                if move.to_square > move.from_square:
                                    extra["rook_from"] = move.to_square + 1
                                    extra["rook_to"] = move.to_square - 1
                                else:
                                    extra["rook_from"] = move.to_square - 2
                                    extra["rook_to"] = move.to_square + 1
                            if game.board.is_en_passant(move):
                                extra["captured_sq"] = chess.square(
                                    chess.square_file(move.to_square),
                                    chess.square_rank(move.from_square)
                                )
                            anim_active = True
                            anim_move = move
                            anim_start_time = time.time()
                            anim_duration = 0.25
                            anim_extra = extra
                            game.selected_square = None
                        elif game.pending_promotion:
                            promotion_buttons = None

        # ── Frame update ──
        if state == PLAYING:
            game.update_clocks()

            # 1. Animation completion — execute move after animation finishes
            if anim_active:
                elapsed = time.time() - anim_start_time
                if elapsed >= anim_duration:
                    game._execute_move(anim_move)
                    anim_active = False
                    anim_move = None
                    if game.is_game_over():
                        bot_move_pending = False
                        bot_pending_move = None
                    elif self_play:
                        bot_move_pending = True
                        bot_pending_move = None
                    elif vs_bot and not self_play \
                            and game.board.turn != game.player_color:
                        bot_move_pending = True
                        bot_pending_move = None
                    else:
                        bot_move_pending = False
                        bot_pending_move = None

            # 2. Bot delay expired → start animation
            if not anim_active and bot_move_pending and bot_pending_move is not None \
                    and time.time() >= bot_ready_time:
                extra = {}
                m = bot_pending_move
                piece = game.board.piece_at(m.from_square)
                if piece and piece.piece_type == chess.KING \
                        and abs(m.to_square - m.from_square) == 2:
                    if m.to_square > m.from_square:
                        extra["rook_from"] = m.to_square + 1
                        extra["rook_to"] = m.to_square - 1
                    else:
                        extra["rook_from"] = m.to_square - 2
                        extra["rook_to"] = m.to_square + 1
                if game.board.is_en_passant(m):
                    extra["captured_sq"] = chess.square(
                        chess.square_file(m.to_square),
                        chess.square_rank(m.from_square)
                    )
                anim_active = True
                anim_move = m
                anim_start_time = time.time()
                anim_duration = 0.25
                anim_extra = extra
                bot_pending_move = None

            # 3. Bot search kickoff
            if not anim_active and bot_move_pending and bot_pending_move is None \
                    and not bot_search_running:
                board_copy = game.board.copy()
                max_time = 0.8 + engine.depth * 0.5
                active_engine = engine
                if self_play:
                    active_engine = engine_white if game.board.turn == chess.WHITE else engine_black
                bot_search_result_container = []
                bot_search_thread = threading.Thread(
                    target=_bot_search_worker,
                    args=(active_engine, board_copy, max_time, bot_search_result_container),
                    daemon=True,
                )
                bot_search_thread.start()
                bot_search_running = True

            # 4. Bot search result collection
            if not anim_active and bot_search_running and bot_search_thread \
                    and not bot_search_thread.is_alive():
                bot_search_running = False
                bot_pending_move = bot_search_result_container[0] if bot_search_result_container else None
                if bot_pending_move is None:
                    bot_move_pending = False
                else:
                    bot_ready_time = time.time() + (self_play_delay if self_play else bot_delay)

        # ── Render FIRST (player's move shows instantly) ──
        if state != prev_state:
            fade_active = True
            fade_start = time.time()
        screen.fill(constants.THEME["bg"])

        if state == MAIN_MENU:
            play_rect, settings_rect = draw_main_menu(screen)
            if mouse_pos:
                if play_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, play_rect)
                elif settings_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, settings_rect)
        elif state == SETTINGS_LIST:
            buttons, back_rect = draw_settings_list(screen, settings)
            if mouse_pos:
                for rect, label, enabled in buttons:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                if back_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, back_rect)
        elif state == TIME_SELECTOR:
            preset_buttons, mins_controls, inc_controls, save_rect, back_btn_rect = \
                draw_time_selector(screen, settings)
            if mouse_pos:
                for rect, mins, inc in preset_buttons:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                for rect, kind, val in mins_controls:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                for rect, kind, val in inc_controls:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                if save_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, save_rect)
                elif back_btn_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, back_btn_rect)
        elif state == MODE_SELECT:
            bot_rect, self_play_rect, player_rect, back_rect = draw_mode_select(screen, settings)
            if mouse_pos:
                if bot_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, bot_rect)
                elif self_play_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, self_play_rect)
                elif player_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, player_rect)
                elif back_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, back_rect)
        elif state == COLOR_CHOICE:
            w_rect, b_rect, back_rect = draw_color_choice(screen)
            if mouse_pos:
                if w_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, w_rect)
                elif b_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, b_rect)
                elif back_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, back_rect)
        elif state == BOT_VERSION_SELECTOR:
            version_buttons, back_rect = draw_bot_version_selector(screen, settings)
            if mouse_pos:
                for rect, idx in version_buttons:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                if back_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, back_rect)
        elif state == BOT_DEPTH_SELECTOR:
            preset_buttons, depth_controls, save_rect, back_btn_rect = \
                draw_bot_depth_selector(screen, settings)
            if mouse_pos:
                for rect, d in preset_buttons:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                for rect, val in depth_controls:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                if save_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, save_rect)
                elif back_btn_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, back_btn_rect)
        elif state == SELF_PLAY_CONFIG:
            buttons = draw_self_play_config(screen, settings, self_play_white_ver, self_play_black_ver, self_play_delay)
            if mouse_pos:
                for key in ("white", "black"):
                    for rect, vi in buttons[key]:
                        if rect.collidepoint(mouse_pos):
                            _draw_hover_border(screen, rect)
                            break
                for rect, d in buttons["delay"]:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                if buttons["start"].collidepoint(mouse_pos):
                    _draw_hover_border(screen, buttons["start"])
                elif buttons["back"].collidepoint(mouse_pos):
                    _draw_hover_border(screen, buttons["back"])
        elif state == BOARD_THEME_SELECTOR:
            theme_buttons, back_rect = draw_board_theme_selector(screen, settings)
            if mouse_pos:
                for rect, idx in theme_buttons:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                if back_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, back_rect)
        elif state == PIECE_STYLE_SELECTOR:
            style_buttons, back_rect = draw_piece_style_selector(screen, settings)
            if mouse_pos:
                for rect, idx in style_buttons:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                if back_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, back_rect)
        elif state == BOOK_SELECTOR:
            book_buttons, back_rect, dl_rect = draw_book_selector(screen, settings, pending_idx=_book_pending_dl)
            if mouse_pos:
                for rect, idx in book_buttons:
                    if rect.collidepoint(mouse_pos):
                        _draw_hover_border(screen, rect)
                        break
                if back_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, back_rect)
                elif dl_rect and dl_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, dl_rect)
            if _book_download_active and _book_download_idx is not None and _book_download_idx in _book_download_progress:
                pct = _book_download_progress.get(_book_download_idx, 0)
                font = pygame.font.SysFont("Segoe UI", 14)
                if pct == -1:
                    msg = "Extracting..."
                elif pct == -2:
                    msg = "Download failed!"
                else:
                    msg = f"Downloading... {pct}%"
                txt = font.render(msg, True, constants.THEME["btn_accent_text"])
                screen.blit(txt, (constants.WINDOW_WIDTH // 2 - 60, constants.WINDOW_HEIGHT - 90))
            elif not _book_download_active and _book_download_idx is not None and _book_download_progress.get(_book_download_idx) == 100:
                font = pygame.font.SysFont("Segoe UI", 14)
                txt = font.render("Download complete! Click the book to select it.", True, constants.THEME["btn_accent_border"])
                screen.blit(txt, (constants.WINDOW_WIDTH // 2 - 120, constants.WINDOW_HEIGHT - 90))
        elif state == PLAYING:
            if not (game.is_game_over() or game.resigned):
                game_over_pgn_copied = False

            check_square = None
            if game.board.is_check():
                king_sq = game.board.king(game.board.turn)
                check_square = king_sq

            legal_moves = None
            if game.selected_square is not None and not game.pending_promotion:
                legal_moves = game.get_legal_moves_for_square(game.selected_square)

            theme = constants.BOARD_THEMES[settings.board_theme]["colors"]
            anim_data = None
            if anim_active and anim_move is not None:
                elapsed = time.time() - anim_start_time
                progress = min(1.0, elapsed / anim_duration)
                anim_data = {
                    "active": True,
                    "from_sq": anim_move.from_square,
                    "to_sq": anim_move.to_square,
                    "progress": progress,
                    "extra": anim_extra,
                }
            board_view.draw(
                screen,
                game.board,
                selected_square=game.selected_square,
                legal_moves=legal_moves,
                last_move=game.last_move,
                check_square=check_square,
                theme_colors=theme,
                anim_data=anim_data,
            )

            if not self_play:
                resign_rect, scroll_offset = draw_panel(
                    screen, game, board_view, scroll_offset
                )
                if mouse_pos and resign_rect.collidepoint(mouse_pos):
                    _draw_hover_border(screen, resign_rect)
            else:
                resign_rect = pygame.Rect(0, 0, 1, 1)
                draw_panel(screen, game, board_view, scroll_offset, self_play=True)

            if bot_move_pending and not anim_active:
                font = pygame.font.SysFont("Segoe UI", 18, bold=True)
                dots = "." * (int(time.time() * 3) % 4)
                if self_play:
                    who = "White" if game.board.turn == chess.WHITE else "Black"
                    label = font.render(f"{who} is thinking{dots}", True, constants.THEME["thinking_text"])
                else:
                    label = font.render(f"VECTOR is thinking{dots}", True, constants.THEME["thinking_text"])
                lr = label.get_rect(
                    center=(
                        constants.WINDOW_WIDTH - constants.PANEL_WIDTH // 2,
                        552
                    )
                )
                screen.blit(label, lr)

            if game.pending_promotion:
                promotion_buttons = draw_promotion_dialog(screen, game)

            if game.is_game_over() or game.resigned:
                overlay = pygame.Surface((
                    constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT
                ))
                overlay.set_alpha(180)
                overlay.fill(constants.THEME["overlay"])
                screen.blit(overlay, (0, 0))

                result = game.game_result()
                result_font = pygame.font.SysFont("Segoe UI", 28, bold=True)
                result_text = result_font.render(result, True, constants.THEME["text_bright"])
                result_rect = result_text.get_rect(
                    center=(constants.WINDOW_WIDTH // 2,
                            constants.WINDOW_HEIGHT // 2 - 45)
                )
                screen.blit(result_text, result_rect)

                prompt_font = pygame.font.SysFont("Segoe UI", 15)
                prompt = prompt_font.render(
                    "'n' Menu  |  Esc Quit",
                    True, constants.THEME["text_dim"]
                )
                prompt_rect = prompt.get_rect(
                    center=(constants.WINDOW_WIDTH // 2,
                            constants.WINDOW_HEIGHT // 2 + 10)
                )
                screen.blit(prompt, prompt_rect)

                pgn_btn_color = constants.THEME["btn_accent_fill"] if not game_over_pgn_copied else constants.THEME["btn_inactive_fill"]
                pgn_font = pygame.font.SysFont("Segoe UI", 16)
                pgn_label = pgn_font.render(
                    "Copy PGN" if not game_over_pgn_copied else "Copied!",
                    True, constants.THEME["btn_accent_text"] if not game_over_pgn_copied else constants.THEME["btn_inactive_text"]
                )
                pgn_btn_rect = pygame.Rect(0, 0, 120, 32)
                pgn_btn_rect.center = (
                    constants.WINDOW_WIDTH // 2,
                    constants.WINDOW_HEIGHT // 2 + 50
                )
                pygame.draw.rect(screen, pgn_btn_color, pgn_btn_rect, border_radius=4)
                screen.blit(pgn_label, pgn_label.get_rect(center=pgn_btn_rect.center))

        if fade_active:
            elapsed = time.time() - fade_start
            if elapsed >= fade_duration:
                fade_active = False
            else:
                alpha = int(255 * (1.0 - elapsed / fade_duration))
                overlay = pygame.Surface((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
                overlay.set_alpha(alpha)
                overlay.fill(constants.THEME["overlay"])
                screen.blit(overlay, (0, 0))

        prev_state = state
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
