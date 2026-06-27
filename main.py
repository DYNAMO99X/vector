import sys
import time
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
    BOT_VERSIONS,
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


def draw_panel(screen, game, board_view, scroll_offset):
    panel_rect = pygame.Rect(constants.PANEL_X, constants.MARGIN_TOP,
                             constants.PANEL_WIDTH, constants.BOARD_SIZE)
    pygame.draw.rect(screen, constants.PANEL_BG, panel_rect)
    pygame.draw.rect(screen, constants.PANEL_BORDER, panel_rect, 2)

    font = pygame.font.SysFont("Segoe UI", 18, bold=True)
    font_big = pygame.font.SysFont("Segoe UI", 16)
    font_small = pygame.font.SysFont("Segoe UI", 13)
    font_header = pygame.font.SysFont("Segoe UI", 22, bold=True)

    x = panel_rect.x + 15
    w = panel_rect.width - 30

    title = font_header.render("VECTOR", True, (220, 220, 220))
    screen.blit(title, (x, panel_rect.y + 10))

    subtitle = font_small.render("Vibe-Engineered Chess", True, constants.TEXT_DIM)
    screen.blit(subtitle, (x, panel_rect.y + 38))

    top = panel_rect.y + 68

    turn_text = font.render(
        f"Turn: {'White' if game.board.turn == chess.WHITE else 'Black'}",
        True, constants.TEXT_COLOR
    )
    screen.blit(turn_text, (x, top))

    clock_y = top + 32
    w_time = game.player_time if game.player_color == chess.WHITE else game.opponent_time
    b_time = game.opponent_time if game.player_color == chess.WHITE else game.player_time
    w_label = "You" if game.player_color == chess.WHITE else "Opp"
    b_label = "Opp" if game.player_color == chess.WHITE else "You"

    w_min, w_sec = divmod(int(w_time), 60)
    b_min, b_sec = divmod(int(b_time), 60)
    w_str = f"{w_label}: {w_min:02d}:{w_sec:02d}"
    b_str = f"{b_label}: {b_min:02d}:{b_sec:02d}"

    is_w_turn = game.board.turn == chess.WHITE
    w_color = (255, 255, 200) if is_w_turn else constants.TEXT_COLOR
    b_color = (255, 255, 200) if not is_w_turn else constants.TEXT_COLOR

    wc = font_big.render(w_str, True, w_color)
    screen.blit(wc, (x + 30, clock_y))
    bc = font_big.render(b_str, True, b_color)
    screen.blit(bc, (x + 30, clock_y + 22))

    pip_font = pygame.font.SysFont("Segoe UI Symbol", 14)
    wpip = pip_font.render("\u25CF", True, (240, 240, 240))
    screen.blit(wpip, (x, clock_y))
    bpip = pip_font.render("\u25CF", True, (40, 40, 40))
    screen.blit(bpip, (x, clock_y + 22))

    cap_y = clock_y + 50
    cap_label = font_small.render("Captured", True, constants.TEXT_DIM)
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
        line = font_small.render(color_name, True, constants.TEXT_DIM)
        screen.blit(line, (x, cap_y))
        cap_y += 16
        cap_chars = [
            constants.UNICODE_PIECES.get(f"{prefix}{p.symbol().upper()}", "?")
            for p in sorted_caps
        ]
        piece_font = pygame.font.SysFont("Segoe UI Symbol", 16)
        for start in range(0, len(cap_chars), 8):
            chunk = "".join(cap_chars[start:start + 8])
            r = piece_font.render(chunk, True, constants.TEXT_COLOR)
            screen.blit(r, (x + 5, cap_y))
            cap_y += 20

    moves_label = font.render("Moves", True, constants.TEXT_COLOR)
    moves_y = max(cap_y + 10, panel_rect.y + 300)
    screen.blit(moves_label, (x, moves_y))
    moves_y += 30

    move_area_height = panel_rect.bottom - moves_y - 50
    area_rect = pygame.Rect(x - 5, moves_y - 5, w + 10, move_area_height + 10)
    pygame.draw.rect(screen, (30, 28, 25), area_rect, border_radius=4)

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
            num_text = font_small.render(f"{num}.", True, constants.TEXT_DIM)
            screen.blit(num_text, (x, display_y))
            offset = 28
        else:
            offset = 75

        san_color = constants.TEXT_COLOR if i % 2 == 0 else (180, 180, 180)
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

        pygame.draw.rect(screen, (50, 48, 45),
                         (x + w - 8, scrollbar_y, 6, track_h),
                         border_radius=3)
        pygame.draw.rect(screen, (120, 120, 120),
                         (x + w - 8, thumb_pos, 6, thumb_h),
                         border_radius=3)

    btn_y = panel_rect.bottom - 36
    resign_rect = pygame.Rect(x, btn_y, 80, 28)
    pygame.draw.rect(screen, (80, 50, 50), resign_rect, border_radius=4)
    pygame.draw.rect(screen, (120, 70, 70), resign_rect, 1, border_radius=4)
    resign_text = font_small.render("Resign", True, (200, 140, 140))
    rt_rect = resign_text.get_rect(center=resign_rect.center)
    screen.blit(resign_text, rt_rect)

    return resign_rect, scroll_offset


def draw_promotion_dialog(screen, game):
    overlay = pygame.Surface((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
    overlay.set_alpha(160)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    dialog_w = 360
    dialog_h = 120
    dialog_x = (constants.WINDOW_WIDTH - dialog_w) // 2
    dialog_y = (constants.WINDOW_HEIGHT - dialog_h) // 2

    pygame.draw.rect(screen, (50, 48, 45),
                     (dialog_x, dialog_y, dialog_w, dialog_h),
                     border_radius=8)
    pygame.draw.rect(screen, (100, 100, 100),
                     (dialog_x, dialog_y, dialog_w, dialog_h), 2,
                     border_radius=8)

    font = pygame.font.SysFont("Segoe UI", 16, bold=True)
    prompt = font.render("Choose promotion piece:", True, constants.TEXT_COLOR)
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
        pygame.draw.rect(screen, (70, 68, 65), rect, border_radius=6)
        pygame.draw.rect(screen, (100, 100, 100), rect, 1, border_radius=6)

        pf = pygame.font.SysFont("Segoe UI Symbol", 40)
        unicode_char = constants.UNICODE_PIECES[piece_key]
        text = pf.render(unicode_char, True, (240, 240, 240))
        outline = pf.render(unicode_char, True, (0, 0, 0))

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
        "Keys: Q R B N", True, constants.TEXT_DIM
    )
    hr = hint.get_rect(center=(constants.WINDOW_WIDTH // 2, dialog_y + dialog_h - 10))
    screen.blit(hint, hr)

    return buttons


def draw_mode_select(screen, settings):
    screen.fill(constants.BG_COLOR)

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    title = font_big.render("Select Game Mode", True, (220, 220, 220))
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 140))
    screen.blit(title, tr)

    button_w = 300
    button_h = 80
    btn_x = constants.WINDOW_WIDTH // 2 - button_w // 2

    bot_rect = pygame.Rect(btn_x, 210, button_w, button_h)
    pygame.draw.rect(screen, (40, 65, 55), bot_rect, border_radius=12)
    pygame.draw.rect(screen, (80, 160, 130), bot_rect, 2, border_radius=12)

    bot_title = font_mid.render(
        f"vs VECTOR {BOT_VERSIONS[settings.bot_version][0]}", True, (140, 230, 200)
    )
    bt_rect = bot_title.get_rect(center=(bot_rect.centerx, bot_rect.centery - 12))
    screen.blit(bot_title, bt_rect)

    bot_sub = font_small.render("Play against the engine", True, (140, 190, 170))
    bs_rect = bot_sub.get_rect(center=(bot_rect.centerx, bot_rect.centery + 14))
    screen.blit(bot_sub, bs_rect)

    player_rect = pygame.Rect(btn_x, 320, button_w, button_h)
    pygame.draw.rect(screen, (55, 55, 55), player_rect, border_radius=12)
    pygame.draw.rect(screen, (100, 100, 100), player_rect, 2, border_radius=12)

    pl_title = font_mid.render("vs Player", True, (200, 200, 200))
    pt_rect = pl_title.get_rect(center=(player_rect.centerx, player_rect.centery - 12))
    screen.blit(pl_title, pt_rect)

    pl_sub = font_small.render("Play against a friend locally", True, (150, 150, 150))
    ps_rect = pl_sub.get_rect(center=(player_rect.centerx, player_rect.centery + 14))
    screen.blit(pl_sub, ps_rect)

    back_rect = pygame.Rect(constants.WINDOW_WIDTH // 2 - 50, 450, 100, 36)
    pygame.draw.rect(screen, (65, 65, 65), back_rect, border_radius=6)
    pygame.draw.rect(screen, (100, 100, 100), back_rect, 1, border_radius=6)
    back_text = font_small.render("< Back", True, (180, 180, 180))
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return bot_rect, player_rect, back_rect


def draw_color_choice(screen):
    screen.fill(constants.BG_COLOR)

    font = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 16)

    title = font.render("VECTOR", True, (220, 220, 220))
    title_rect = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 160))
    screen.blit(title, title_rect)

    subtitle = font_small.render(
        "Vibe-Engineered Chess Tactician for Online Rankings",
        True, constants.TEXT_DIM
    )
    sub_rect = subtitle.get_rect(center=(constants.WINDOW_WIDTH // 2, 195))
    screen.blit(subtitle, sub_rect)

    prompt_font = pygame.font.SysFont("Segoe UI", 22)
    prompt = prompt_font.render("Choose your color:", True, constants.TEXT_COLOR)
    prompt_rect = prompt.get_rect(center=(constants.WINDOW_WIDTH // 2, 290))
    screen.blit(prompt, prompt_rect)

    white_rect = pygame.Rect(0, 0, 200, 55)
    white_rect.center = (constants.WINDOW_WIDTH // 2 - 120, 370)
    pygame.draw.rect(screen, (60, 60, 60), white_rect, border_radius=8)
    pygame.draw.rect(screen, (200, 200, 200), white_rect, 2, border_radius=8)
    w_text = font_small.render("Play as White", True, (200, 200, 200))
    w_rect = w_text.get_rect(center=white_rect.center)
    screen.blit(w_text, w_rect)

    black_rect = pygame.Rect(0, 0, 200, 55)
    black_rect.center = (constants.WINDOW_WIDTH // 2 + 120, 370)
    pygame.draw.rect(screen, (60, 60, 60), black_rect, border_radius=8)
    pygame.draw.rect(screen, (100, 100, 100), black_rect, 2, border_radius=8)
    b_text = font_small.render("Play as Black", True, (180, 180, 180))
    b_rect = b_text.get_rect(center=black_rect.center)
    screen.blit(b_text, b_rect)

    back_rect = pygame.Rect(constants.WINDOW_WIDTH // 2 - 50, 460, 100, 36)
    pygame.draw.rect(screen, (65, 65, 65), back_rect, border_radius=6)
    pygame.draw.rect(screen, (100, 100, 100), back_rect, 1, border_radius=6)
    back_text = font_small.render("< Back", True, (180, 180, 180))
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return white_rect, black_rect, back_rect


def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)
    )
    pygame.display.set_caption(constants.SCREEN_TITLE)
    clock = pygame.time.Clock()

    board_view = Board()
    settings = GameSettings()
    game = Game(settings.time_minutes, settings.time_increment)
    engine = Engine(depth=settings.bot_depth, version=settings.bot_version, book_enabled=settings.book_enabled)
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
    bot_need_compute = False

    while running:
        dt = clock.tick(constants.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state == PLAYING:
                    state = MAIN_MENU
                elif state == MODE_SELECT:
                    state = MAIN_MENU
                elif state == SETTINGS_LIST:
                    state = MAIN_MENU
                elif state == TIME_SELECTOR:
                    state = SETTINGS_LIST
                elif state == COLOR_CHOICE:
                    state = MODE_SELECT
                elif state == BOT_VERSION_SELECTOR:
                    state = SETTINGS_LIST
                elif state == BOT_DEPTH_SELECTOR:
                    state = SETTINGS_LIST
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
                    bot_rect, player_rect, back_rect = draw_mode_select(screen, settings)
                    if back_rect.collidepoint(mx, my):
                        state = MAIN_MENU
                    elif bot_rect.collidepoint(mx, my):
                        vs_bot = True
                        state = COLOR_CHOICE
                    elif player_rect.collidepoint(mx, my):
                        vs_bot = False
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
                            elif label == "Opening Book":
                                settings.book_enabled = not settings.book_enabled
                                engine.book_enabled = settings.book_enabled
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
                        board_view.flipped = False
                        state = PLAYING
                        scroll_offset = 0
                        promotion_buttons = None
                        game_over_pgn_copied = False
                        if vs_bot and game.board.turn != game.player_color:
                            bot_move_pending = True
                            bot_pending_move = None
                    elif b_rect.collidepoint(mx, my):
                        game.reset(
                            player_color=chess.BLACK,
                            time_minutes=settings.time_minutes,
                            time_increment=settings.time_increment
                        )
                        board_view.flipped = True
                        state = PLAYING
                        scroll_offset = 0
                        promotion_buttons = None
                        game_over_pgn_copied = False
                        if vs_bot and game.board.turn != game.player_color:
                            bot_move_pending = True
                            bot_pending_move = None
                continue

            if state == PLAYING:
                if bot_move_pending or (vs_bot and game.board.turn != game.player_color):
                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        board_view.flip()
                        continue
                    if event.key == pygame.K_n:
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
                            game.choose_promotion(key_map[event.key])
                            promotion_buttons = None
                            continue
                    if event.type == pygame.MOUSEBUTTONDOWN and promotion_buttons:
                        mx, my = event.pos
                        for rect, piece_type in promotion_buttons:
                            if rect.collidepoint(mx, my):
                                game.choose_promotion(piece_type)
                                promotion_buttons = None
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
                        game.try_move(game.selected_square, square)
                        if game.pending_promotion:
                            promotion_buttons = None
                        elif vs_bot and not game.is_game_over():
                            bot_move_pending = True
                            bot_pending_move = None

        # ── Frame update (no heavy compute yet) ──
        if state == PLAYING:
            game.update_clocks()

            if (bot_move_pending and bot_pending_move is not None
                    and time.time() >= bot_ready_time):
                game._execute_move(bot_pending_move)
                bot_move_pending = False
                bot_pending_move = None

            if bot_move_pending and bot_pending_move is None and not bot_need_compute:
                bot_need_compute = True

        # ── Render FIRST (player's move shows instantly) ──
        screen.fill(constants.BG_COLOR)

        if state == MAIN_MENU:
            draw_main_menu(screen)
        elif state == SETTINGS_LIST:
            draw_settings_list(screen, settings)
        elif state == TIME_SELECTOR:
            draw_time_selector(screen, settings)
        elif state == MODE_SELECT:
            draw_mode_select(screen, settings)
        elif state == COLOR_CHOICE:
            draw_color_choice(screen)
        elif state == BOT_VERSION_SELECTOR:
            draw_bot_version_selector(screen, settings)
        elif state == BOT_DEPTH_SELECTOR:
            draw_bot_depth_selector(screen, settings)
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

            board_view.draw(
                screen,
                game.board,
                selected_square=game.selected_square,
                legal_moves=legal_moves,
                last_move=game.last_move,
                check_square=check_square,
            )

            resign_rect, scroll_offset = draw_panel(
                screen, game, board_view, scroll_offset
            )

            if bot_move_pending:
                font = pygame.font.SysFont("Segoe UI", 18, bold=True)
                label = font.render("VECTOR is thinking...", True, (0, 0, 0))
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
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))

                result = game.game_result()
                result_font = pygame.font.SysFont("Segoe UI", 28, bold=True)
                result_text = result_font.render(result, True, (255, 255, 255))
                result_rect = result_text.get_rect(
                    center=(constants.WINDOW_WIDTH // 2,
                            constants.WINDOW_HEIGHT // 2 - 45)
                )
                screen.blit(result_text, result_rect)

                prompt_font = pygame.font.SysFont("Segoe UI", 15)
                prompt = prompt_font.render(
                    "'n' Menu  |  Esc Quit",
                    True, (200, 200, 200)
                )
                prompt_rect = prompt.get_rect(
                    center=(constants.WINDOW_WIDTH // 2,
                            constants.WINDOW_HEIGHT // 2 + 10)
                )
                screen.blit(prompt, prompt_rect)

                pgn_btn_color = (60, 140, 60) if not game_over_pgn_copied else (80, 80, 80)
                pgn_font = pygame.font.SysFont("Segoe UI", 16)
                pgn_label = pgn_font.render(
                    "Copy PGN" if not game_over_pgn_copied else "Copied!",
                    True, (255, 255, 255)
                )
                pgn_btn_rect = pygame.Rect(0, 0, 120, 32)
                pgn_btn_rect.center = (
                    constants.WINDOW_WIDTH // 2,
                    constants.WINDOW_HEIGHT // 2 + 50
                )
                pygame.draw.rect(screen, pgn_btn_color, pgn_btn_rect, border_radius=4)
                screen.blit(pgn_label, pgn_label.get_rect(center=pgn_btn_rect.center))

        pygame.display.flip()

        # ── Heavy compute AFTER render (never blocks player's move display) ──
        if state == PLAYING and bot_need_compute:
            max_time = 0.8 + engine.depth * 0.5
            bot_pending_move = engine.find_move(game.board, max_time=max_time)
            bot_need_compute = False
            if bot_pending_move is None:
                bot_move_pending = False
            else:
                bot_ready_time = time.time() + bot_delay

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
