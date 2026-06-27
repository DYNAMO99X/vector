import os
import pygame
import constants

TIME_PRESETS = [
    ("1+0", 1, 0),
    ("3+0", 3, 0),
    ("5+0", 5, 0),
    ("5+3", 5, 3),
    ("10+0", 10, 0),
    ("15+10", 15, 10),
    ("30+0", 30, 0),
    ("60+0", 60, 0),
]

BOT_VERSIONS = [
    ("Mark 1", "Alpha-beta + material/PST"),
    ("Mark 2", "Move ordering + iterative deepening"),
    ("Mark 3", "Quiescence search + advanced evaluation"),
    ("Mark 4", "Aspiration windows + LMR + history/killer"),
    ("Mark 5", "IID + SEE + razoring + futility"),
]

DEPTH_PRESETS = [2, 3, 4, 5, 6, 8, 10]

BASE_URL = "https://github.com/ChrisWhittington/polyglot-books/releases/latest/download"
CEREBELLUM_URL = "https://github.com/gmcheems-org/free-opening-books/raw/main/books/bin/Cerebellum_Light_3Merge_200916.7z"

OPENING_BOOKS = [
    ("Komodo", "komodo.bin", "8.8 MB", "578K", "Salvo Spitaleri",
     f"{BASE_URL}/komodo.zip", True),
    ("Rebel (default)", "book.bin", "169.7 MB", "11.1M", "Jeroen Noomen",
     f"{BASE_URL}/book.zip", True),
    ("UHO Pohl", "uho-pohl.bin", "76.7 MB", "5.0M", "Stefan Pohl",
     f"{BASE_URL}/uho-pohl.zip", True),
    ("CodeKiddy", "codekiddy.bin", "15.7 MB", "1.0M", "CodeKiddy",
     f"{BASE_URL}/codekiddy.zip", True),
    ("DCbook Large", "DCbook_large.bin", "6.1 MB", "398K", "CodeKiddy",
     f"{BASE_URL}/DCbook_large.zip", True),
    ("Book CK", "Book-ck.bin", "5.5 MB", "360K", "CodeKiddy",
     f"{BASE_URL}/Book-ck.zip", True),
    ("Gavi Book", "gavibook.bin", "5.1 MB", "334K", "CodeKiddy",
     f"{BASE_URL}/gavibook.zip", True),
    ("Komodo Variety", "KomodoVariety.bin", "4.1 MB", "267K", "CodeKiddy",
     f"{BASE_URL}/KomodoVariety.zip", True),
    ("Final Book", "final-book.bin", "2.8 MB", "184K", "CodeKiddy",
     f"{BASE_URL}/final-book.zip", True),
    ("Rodent", "rodent.bin", "2.7 MB", "175K", "Pawel Koziol",
     f"{BASE_URL}/rodent.zip", True),
    ("Baron 30", "baron30.bin", "2.5 MB", "163K", "Richard Pijl",
     f"{BASE_URL}/baron30.zip", True),
    ("Elo2400", "Elo2400.bin", "2.4 MB", "156K", "CodeKiddy",
     f"{BASE_URL}/Elo2400.zip", True),
    ("Performance", "Performance.bin", "1.4 MB", "93K", "CodeKiddy",
     f"{BASE_URL}/Performance.zip", True),
    ("Varied", "varied.bin", "1.4 MB", "92K", "CodeKiddy",
     f"{BASE_URL}/varied.zip", True),
    ("Gavi Book Small", "gavibook-small.bin", "0.68 MB", "45K", "CodeKiddy",
     f"{BASE_URL}/gavibook-small.zip", True),
    ("Jeroen", "Jeroen.bin", "0.64 MB", "42K", "Jeroen Noomen",
     f"{BASE_URL}/Jeroen.zip", True),
    ("Fruit", "fruit.bin", "0.48 MB", "31K", "Fruit engine",
     f"{BASE_URL}/fruit.zip", True),
    ("GM 2001", "gm2001.bin", "0.46 MB", "30K", "Oliver Deville",
     f"{BASE_URL}/gm2001.zip", True),
    ("GM 2600", "gm2600.bin", "0.33 MB", "22K", "CodeKiddy",
     f"{BASE_URL}/gm2600.zip", True),
    ("Daring", "Daring.bin", "0.29 MB", "19K", "Jeroen Noomen",
     f"{BASE_URL}/Daring.zip", True),
    ("Rebel Select", "Rebel.bin", "0.29 MB", "19K", "Jeroen Noomen",
     f"{BASE_URL}/Rebel.zip", True),
    ("Variety", "Variety.bin", "0.17 MB", "11K", "Jeroen Noomen",
     f"{BASE_URL}/Variety.zip", True),
    ("Cerebellum Light", "Cerebellum_Light_3Merge_200916.bin", "~? MB", "10.9M", "Cerebellum",
     CEREBELLUM_URL, True),
]

BOOKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "books")


def get_book_status(filename):
    full = os.path.join(BOOKS_DIR, filename)
    return "In Use" if os.path.exists(full) else "Not Downloaded"


class GameSettings:
    def __init__(self):
        self.time_minutes = 10
        self.time_increment = 0
        self.bot_version = 0
        self.bot_depth = 3
        self.book_enabled = True
        self.book_name = "Komodo"
        self.book_filename = "komodo.bin"
        self.board_theme = 0
        self.piece_style = 0
        self.theme = "dark"

    def reset(self):
        self.time_minutes = 10
        self.time_increment = 0
        self.bot_version = 0
        self.bot_depth = 3
        self.book_enabled = True
        self.book_name = "Komodo"
        self.book_filename = "komodo.bin"
        self.board_theme = 0
        self.piece_style = 0
        self.theme = "dark"

    def total_seconds(self):
        return self.time_minutes * 60


def draw_main_menu(screen):
    screen.fill(constants.THEME["bg"])

    font_big = pygame.font.SysFont("Segoe UI", 48, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    title = font_big.render("VECTOR", True, constants.THEME["text_bright"])
    title_rect = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 180))
    screen.blit(title, title_rect)

    glow = font_big.render("VECTOR", True, (60, 180, 200))
    for dx, dy in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
        screen.blit(glow, (title_rect.x + dx, title_rect.y + dy))
    screen.blit(title, title_rect)

    subtitle = font_small.render(
        "Vibe-Engineered Chess Tactician for Online Rankings",
        True, constants.THEME["text_dim"]
    )
    sr = subtitle.get_rect(center=(constants.WINDOW_WIDTH // 2, 225))
    screen.blit(subtitle, sr)

    button_w = 220
    button_h = 55
    btn_x = constants.WINDOW_WIDTH // 2 - button_w // 2

    play_rect = pygame.Rect(btn_x, 310, button_w, button_h)
    pygame.draw.rect(screen, constants.THEME["btn_accent_fill"], play_rect, border_radius=10)
    pygame.draw.rect(screen, constants.THEME["btn_accent_border"], play_rect, 2, border_radius=10)
    play_text = font_mid.render("Play", True, constants.THEME["btn_accent_text"])
    pt_rect = play_text.get_rect(center=play_rect.center)
    screen.blit(play_text, pt_rect)

    settings_rect = pygame.Rect(btn_x, 385, button_w, button_h)
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], settings_rect, border_radius=10)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], settings_rect, 2, border_radius=10)
    stext = font_mid.render("Settings", True, constants.THEME["btn_back_text"])
    st_rect = stext.get_rect(center=settings_rect.center)
    screen.blit(stext, st_rect)

    return play_rect, settings_rect


def draw_settings_list(screen, settings):
    screen.fill(constants.THEME["bg"])

    font_big = pygame.font.SysFont("Segoe UI", 32, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 18)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    title = font_big.render("Settings", True, constants.THEME["text_title"])
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 80))
    screen.blit(title, tr)

    items = [
        ("Match Time", "Set game timer and increment", True),
        ("Bot Version", f"Currently: {BOT_VERSIONS[settings.bot_version][0]}", True),
        ("Bot Depth", f"Search depth: {settings.bot_depth}", True),
        ("Piece Style", f"Style: {constants.PIECE_STYLES[settings.piece_style][0]}", True),
        ("Opening Book", f"Book: {settings.book_name}", True),
        ("Board Theme", f"Theme: {constants.BOARD_THEMES[settings.board_theme]['name']}", True),
        ("Theme", f"Mode: {settings.theme.title()}", True),
    ]

    buttons = []
    start_y = 130
    for i, (label, desc, enabled) in enumerate(items):
        y = start_y + i * 80
        rect = pygame.Rect(
            constants.WINDOW_WIDTH // 2 - 200, y, 400, 60
        )
        color = constants.THEME["btn_row_fill"] if enabled else constants.THEME["btn_inactive_fill"]
        border = constants.THEME["btn_row_border"] if enabled else constants.THEME["btn_inactive_border"]
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 2, border_radius=8)

        text_color = constants.THEME["btn_row_text"] if enabled else constants.THEME["btn_inactive_text"]
        lbl = font_mid.render(label, True, text_color)
        screen.blit(lbl, (rect.x + 20, rect.y + 10))

        d = font_small.render(desc, True, constants.THEME["btn_row_text_dim"] if enabled else constants.THEME["btn_inactive_text_dim"])
        screen.blit(d, (rect.x + 20, rect.y + 33))

        if enabled:
            arrow = font_mid.render(">", True, constants.THEME["btn_accent_border"])
            screen.blit(arrow, (rect.right - 25, rect.y + 18))

        buttons.append((rect, label, enabled))

    back_rect = pygame.Rect(30, 30, 100, 36)
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], back_rect, border_radius=6)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], back_rect, 1, border_radius=6)
    back_text = font_mid.render("< Back", True, constants.THEME["btn_back_text"])
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return buttons, back_rect


def draw_time_selector(screen, settings):
    screen.fill(constants.THEME["bg"])

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_button = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 14)
    font_clock = pygame.font.SysFont("Segoe UI", 72, bold=True)

    title = font_big.render("Time Control", True, constants.THEME["text_title"])
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 50))
    screen.blit(title, tr)

    time_display = pygame.Rect(
        constants.WINDOW_WIDTH // 2 - 150, 80, 300, 110
    )
    pygame.draw.rect(screen, constants.THEME["display_bg"], time_display, border_radius=12)
    pygame.draw.rect(screen, constants.THEME["btn_accent_border"], time_display, 2, border_radius=12)

    time_str = f"{settings.time_minutes:02d} : {settings.time_increment:02d}"
    clock_text = font_clock.render(time_str, True, constants.THEME["btn_accent_text"])
    ct_rect = clock_text.get_rect(center=(time_display.centerx - 3, time_display.centery - 16))
    screen.blit(clock_text, ct_rect)

    label_m = font_small.render("Minutes", True, constants.THEME["text_dim"])
    screen.blit(label_m, (time_display.centerx - 78, time_display.bottom - 28))
    label_i = font_small.render("Increment", True, constants.THEME["text_dim"])
    screen.blit(label_i, (time_display.centerx + 22, time_display.bottom - 28))

    preset_buttons = []
    cols = 4
    pw = 95
    ph = 38
    gap = 10
    total_w = cols * pw + (cols - 1) * gap
    start_x = constants.WINDOW_WIDTH // 2 - total_w // 2
    start_y = 220

    for idx, (label, mins, inc) in enumerate(TIME_PRESETS):
        col = idx % cols
        row = idx // cols
        rx = start_x + col * (pw + gap)
        ry = start_y + row * (ph + gap)
        rect = pygame.Rect(rx, ry, pw, ph)
        is_active = (mins == settings.time_minutes and
                     inc == settings.time_increment)
        bg = constants.THEME["btn_accent_fill"] if is_active else constants.THEME["btn_inactive_fill"]
        border = constants.THEME["btn_accent_border"] if is_active else constants.THEME["btn_inactive_border"]
        pygame.draw.rect(screen, bg, rect, border_radius=6)
        pygame.draw.rect(screen, border, rect, 2, border_radius=6)
        text = font_button.render(label, True,
                                   constants.THEME["btn_accent_text"] if is_active else constants.THEME["btn_inactive_text"])
        t_rect = text.get_rect(center=rect.center)
        screen.blit(text, t_rect)
        preset_buttons.append((rect, mins, inc))

    adjust_y = start_y + 2 * (ph + gap) + 20

    adjust_font = pygame.font.SysFont("Segoe UI", 14, bold=True)

    controls = []
    mins_title = font_small.render("Minutes", True, constants.THEME["text"])
    screen.blit(mins_title, (constants.WINDOW_WIDTH // 2 - 160, adjust_y))

    mins_controls = []
    for val, label in [(-5, "-5"), (-1, "-1"), (1, "+1"), (5, "+5")]:
        bx = constants.WINDOW_WIDTH // 2 - 160 + (list.index([-5, -1, 1, 5], val)) * 80
        by = adjust_y + 22
        rect = pygame.Rect(bx, by, 70, 32)
        pygame.draw.rect(screen, constants.THEME["btn_row_fill"], rect, border_radius=6)
        pygame.draw.rect(screen, constants.THEME["btn_row_border"], rect, 1, border_radius=6)
        text = adjust_font.render(label, True, constants.THEME["btn_row_text"])
        t_rect = text.get_rect(center=rect.center)
        screen.blit(text, t_rect)
        mins_controls.append((rect, "minutes", val))

    inc_y = adjust_y + 65
    inc_title = font_small.render("Increment (sec)", True, constants.THEME["text"])
    screen.blit(inc_title, (constants.WINDOW_WIDTH // 2 - 160, inc_y))

    inc_controls = []
    for val, label in [(-1, "-1"), (1, "+1")]:
        bx = constants.WINDOW_WIDTH // 2 - 80 + list.index([-1, 1], val) * 90
        by = inc_y + 22
        rect = pygame.Rect(bx, by, 70, 32)
        pygame.draw.rect(screen, constants.THEME["btn_row_fill"], rect, border_radius=6)
        pygame.draw.rect(screen, constants.THEME["btn_row_border"], rect, 1, border_radius=6)
        text = adjust_font.render(label, True, constants.THEME["btn_row_text"])
        t_rect = text.get_rect(center=rect.center)
        screen.blit(text, t_rect)
        inc_controls.append((rect, "increment", val))

    btn_y = constants.WINDOW_HEIGHT - 70

    save_rect = pygame.Rect(
        constants.WINDOW_WIDTH // 2 - 110, btn_y, 100, 42
    )
    pygame.draw.rect(screen, constants.THEME["btn_accent_fill"], save_rect, border_radius=8)
    pygame.draw.rect(screen, constants.THEME["btn_accent_border"], save_rect, 2, border_radius=8)
    save_text = font_mid.render("Save", True, constants.THEME["btn_accent_text"])
    st_rect = save_text.get_rect(center=save_rect.center)
    screen.blit(save_text, st_rect)

    back_btn_rect = pygame.Rect(
        constants.WINDOW_WIDTH // 2 + 20, btn_y, 100, 42
    )
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], back_btn_rect, border_radius=8)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], back_btn_rect, 2, border_radius=8)
    back_text = font_mid.render("Back", True, constants.THEME["btn_back_text"])
    btr = back_text.get_rect(center=back_btn_rect.center)
    screen.blit(back_text, btr)

    return preset_buttons, mins_controls, inc_controls, save_rect, back_btn_rect


def handle_time_click(settings, mx, my, preset_buttons,
                      mins_controls, inc_controls, save_rect):
    for rect, mins, inc in preset_buttons:
        if rect.collidepoint(mx, my):
            settings.time_minutes = mins
            settings.time_increment = inc
            return None

    for rect, kind, val in mins_controls:
        if rect.collidepoint(mx, my):
            new_mins = max(1, min(120, settings.time_minutes + val))
            settings.time_minutes = new_mins
            return None

    for rect, kind, val in inc_controls:
        if rect.collidepoint(mx, my):
            new_inc = max(0, min(60, settings.time_increment + val))
            settings.time_increment = new_inc
            return None

    if save_rect.collidepoint(mx, my):
        return "save"

    return None


def draw_bot_version_selector(screen, settings):
    screen.fill(constants.THEME["bg"])

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    title = font_big.render("Bot Version", True, constants.THEME["text_title"])
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 50))
    screen.blit(title, tr)

    current = settings.bot_version
    version_buttons = []

    for idx, (name, desc) in enumerate(BOT_VERSIONS):
        y = 120 + idx * 110
        rect = pygame.Rect(
            constants.WINDOW_WIDTH // 2 - 220, y, 440, 90
        )
        is_active = idx == current
        bg = constants.THEME["btn_accent_fill"] if is_active else constants.THEME["btn_inactive_fill"]
        border = constants.THEME["btn_accent_border"] if is_active else constants.THEME["btn_inactive_border"]
        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)

        color = constants.THEME["btn_accent_text"] if is_active else constants.THEME["text_bright"]
        lbl = font_mid.render(name, True, color)
        screen.blit(lbl, (rect.x + 25, rect.y + 18))

        d = font_small.render(desc, True, constants.THEME["text_dim"] if is_active else constants.THEME["btn_inactive_text_dim"])
        screen.blit(d, (rect.x + 25, rect.y + 50))

        if is_active:
            check = font_mid.render("✔", True, constants.THEME["btn_accent_border"])
            screen.blit(check, (rect.right - 35, rect.y + 28))

        version_buttons.append((rect, idx))

    back_rect = pygame.Rect(30, 30, 100, 36)
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], back_rect, border_radius=6)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], back_rect, 1, border_radius=6)
    back_text = font_small.render("< Back", True, constants.THEME["btn_back_text"])
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return version_buttons, back_rect


def draw_bot_depth_selector(screen, settings):
    screen.fill(constants.THEME["bg"])

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_button = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 14)
    font_display = pygame.font.SysFont("Segoe UI", 72, bold=True)

    title = font_big.render("Bot Depth", True, constants.THEME["text_title"])
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 50))
    screen.blit(title, tr)

    depth_display = pygame.Rect(
        constants.WINDOW_WIDTH // 2 - 150, 80, 300, 110
    )
    pygame.draw.rect(screen, constants.THEME["display_bg"], depth_display, border_radius=12)
    pygame.draw.rect(screen, constants.THEME["btn_accent_border"], depth_display, 2, border_radius=12)

    depth_text = font_display.render(str(settings.bot_depth), True, constants.THEME["btn_accent_text"])
    dt_rect = depth_text.get_rect(center=(depth_display.centerx, depth_display.centery - 10))
    screen.blit(depth_text, dt_rect)

    label_d = font_small.render("Ply depth", True, constants.THEME["text_dim"])
    screen.blit(label_d, (depth_display.centerx - 28, depth_display.bottom - 28))

    preset_buttons = []
    cols = 4
    pw = 95
    ph = 38
    gap = 10
    total_w = cols * pw + (cols - 1) * gap
    start_x = constants.WINDOW_WIDTH // 2 - total_w // 2
    start_y = 230

    for idx, d in enumerate(DEPTH_PRESETS):
        col = idx % cols
        row = idx // cols
        rx = start_x + col * (pw + gap)
        ry = start_y + row * (ph + gap)
        rect = pygame.Rect(rx, ry, pw, ph)
        is_active = d == settings.bot_depth
        bg = constants.THEME["btn_accent_fill"] if is_active else constants.THEME["btn_inactive_fill"]
        border = constants.THEME["btn_accent_border"] if is_active else constants.THEME["btn_inactive_border"]
        pygame.draw.rect(screen, bg, rect, border_radius=6)
        pygame.draw.rect(screen, border, rect, 2, border_radius=6)
        text = font_button.render(str(d), True,
                                   constants.THEME["btn_accent_text"] if is_active else constants.THEME["btn_inactive_text"])
        t_rect = text.get_rect(center=rect.center)
        screen.blit(text, t_rect)
        preset_buttons.append((rect, d))

    adjust_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
    adjust_y = start_y + 2 * (ph + gap) + 30

    depth_controls = []
    for val, label in [(-1, "-1"), (1, "+1")]:
        bx = constants.WINDOW_WIDTH // 2 - 80 + list.index([-1, 1], val) * 90
        by = adjust_y
        rect = pygame.Rect(bx, by, 70, 32)
        pygame.draw.rect(screen, constants.THEME["btn_row_fill"], rect, border_radius=6)
        pygame.draw.rect(screen, constants.THEME["btn_row_border"], rect, 1, border_radius=6)
        text = adjust_font.render(label, True, constants.THEME["btn_row_text"])
        t_rect = text.get_rect(center=rect.center)
        screen.blit(text, t_rect)
        depth_controls.append((rect, val))

    btn_y = constants.WINDOW_HEIGHT - 70

    save_rect = pygame.Rect(
        constants.WINDOW_WIDTH // 2 - 110, btn_y, 100, 42
    )
    pygame.draw.rect(screen, constants.THEME["btn_accent_fill"], save_rect, border_radius=8)
    pygame.draw.rect(screen, constants.THEME["btn_accent_border"], save_rect, 2, border_radius=8)
    save_text = font_mid.render("Save", True, constants.THEME["btn_accent_text"])
    st_rect = save_text.get_rect(center=save_rect.center)
    screen.blit(save_text, st_rect)

    back_btn_rect = pygame.Rect(
        constants.WINDOW_WIDTH // 2 + 20, btn_y, 100, 42
    )
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], back_btn_rect, border_radius=8)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], back_btn_rect, 2, border_radius=8)
    back_text = font_mid.render("Back", True, constants.THEME["btn_back_text"])
    btr = back_text.get_rect(center=back_btn_rect.center)
    screen.blit(back_text, btr)

    return preset_buttons, depth_controls, save_rect, back_btn_rect


def handle_bot_version_click(settings, mx, my, version_buttons, back_rect):
    if back_rect.collidepoint(mx, my):
        return "back"
    for rect, idx in version_buttons:
        if rect.collidepoint(mx, my):
            settings.bot_version = idx
            return None
    return None


def handle_bot_depth_click(settings, mx, my, preset_buttons,
                            depth_controls, save_rect):
    for rect, d in preset_buttons:
        if rect.collidepoint(mx, my):
            settings.bot_depth = d
            return None

    for rect, val in depth_controls:
        if rect.collidepoint(mx, my):
            idx = max(0, min(len(DEPTH_PRESETS) - 1,
                             DEPTH_PRESETS.index(settings.bot_depth) + val))
            settings.bot_depth = DEPTH_PRESETS[idx]
            return None

    if save_rect.collidepoint(mx, my):
        return "save"

    return None


def draw_book_selector(screen, settings, pending_idx=None):
    screen.fill(constants.THEME["bg"])

    font_big = pygame.font.SysFont("Segoe UI", 26, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 16)
    font_small = pygame.font.SysFont("Segoe UI", 13)

    title = font_big.render("Opening Books", True, constants.THEME["text_title"])
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 35))
    screen.blit(title, tr)

    header_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
    headers = ["Book", "Size", "Entries", "Author", "Status"]
    col_x = [30, 360, 460, 540, 700]
    for i, h in enumerate(headers):
        hd = header_font.render(h, True, constants.THEME["text_dim"])
        screen.blit(hd, (col_x[i], 70))

    book_buttons = []
    row_h = 38
    max_visible = 14
    start_y = 90
    num_books = len(OPENING_BOOKS)
    scroll = getattr(draw_book_selector, "_scroll", 0)
    max_scroll = max(0, num_books - max_visible)
    scroll = max(0, min(scroll, max_scroll))
    draw_book_selector._scroll = scroll

    area_rect = pygame.Rect(10, start_y - 4, constants.WINDOW_WIDTH - 20, row_h * max_visible + 8)
    old_clip = screen.get_clip()
    screen.set_clip(area_rect)

    for idx, (name, filename, size_str, entries_str, author, url, is_archive) in enumerate(OPENING_BOOKS):
        if idx < scroll or idx >= scroll + max_visible:
            continue
        y = start_y + (idx - scroll) * row_h
        is_selected = filename == settings.book_filename
        is_pending = idx == pending_idx
        if is_selected:
            bg = constants.THEME["btn_accent_fill"]
        elif is_pending:
            bg = (65, 65, 45) if constants.THEME is constants.DARK else (210, 205, 180)
        else:
            lighter = (48, 45, 42) if constants.THEME is constants.DARK else (228, 222, 212)
            darker = (44, 41, 38) if constants.THEME is constants.DARK else (222, 216, 206)
            bg = lighter if idx % 2 == 0 else darker
        rect = pygame.Rect(10, y, constants.WINDOW_WIDTH - 20, row_h - 2)
        pygame.draw.rect(screen, bg, rect, border_radius=4)
        if is_selected:
            pygame.draw.rect(screen, constants.THEME["btn_accent_border"], rect, 1, border_radius=4)
        elif is_pending:
            pygame.draw.rect(screen, (200, 180, 80), rect, 1, border_radius=4)

        txt_color = constants.THEME["btn_accent_text"] if is_selected else ((220, 210, 180) if is_pending else constants.THEME["text"])
        lbl = font_mid.render(name[:24], True, txt_color)
        screen.blit(lbl, (col_x[0], y + 8))

        sz = font_small.render(size_str, True, txt_color)
        screen.blit(sz, (col_x[1], y + 8))

        en = font_small.render(entries_str, True, txt_color)
        screen.blit(en, (col_x[2], y + 8))

        au = font_small.render(author[:18], True, txt_color)
        screen.blit(au, (col_x[3], y + 8))

        full = os.path.join(BOOKS_DIR, filename)
        exists = os.path.exists(full)
        status_str = "SELECTED" if is_selected else ("Downloaded" if exists else "Click to dl")
        status_color = constants.THEME["btn_accent_border"] if is_selected else ((160, 200, 160) if exists else (180, 160, 140))
        st = font_small.render(status_str, True, status_color)
        screen.blit(st, (col_x[4], y + 8))

        book_buttons.append((rect, idx))

    screen.set_clip(old_clip)

    if num_books > max_visible:
        scrollbar_x = constants.WINDOW_WIDTH - 16
        scrollbar_y = area_rect.y
        track_h = area_rect.h
        thumb_h = max(20, track_h * max_visible // num_books)
        avail = track_h - thumb_h
        thumb_pos = scrollbar_y + avail * scroll // max_scroll if max_scroll else scrollbar_y
        pygame.draw.rect(screen, constants.THEME["scroll_bg"], (scrollbar_x, scrollbar_y, 8, track_h), border_radius=4)
        pygame.draw.rect(screen, constants.THEME["scroll_thumb"], (scrollbar_x, thumb_pos, 8, thumb_h), border_radius=4)

    font_button = pygame.font.SysFont("Segoe UI", 15, bold=True)
    dl_rect = None
    if pending_idx is not None:
        _, pfn, _, _, _, _, _ = OPENING_BOOKS[pending_idx]
        pfull = os.path.join(BOOKS_DIR, pfn)
        if not os.path.exists(pfull):
            dl_rect = pygame.Rect(constants.WINDOW_WIDTH // 2 - 60, constants.WINDOW_HEIGHT - 50, 120, 36)
            dl_border = constants.THEME["btn_accent_border"]
            dl_fill = (40, 70, 60) if constants.THEME is constants.DARK else (60, 190, 155)
            pygame.draw.rect(screen, dl_fill, dl_rect, border_radius=8)
            pygame.draw.rect(screen, dl_border, dl_rect, 2, border_radius=8)
            dl_text = font_button.render("Download", True, constants.THEME["btn_accent_text"])
            dt_rect = dl_text.get_rect(center=dl_rect.center)
            screen.blit(dl_text, dt_rect)

    back_rect = pygame.Rect(30, constants.WINDOW_HEIGHT - 50, 100, 36)
    if dl_rect:
        back_rect.x = dl_rect.right + 20
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], back_rect, border_radius=6)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], back_rect, 1, border_radius=6)
    back_text = font_mid.render("< Back", True, constants.THEME["btn_back_text"])
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return book_buttons, back_rect, dl_rect


def handle_book_scroll(event_y):
    scroll = getattr(draw_book_selector, "_scroll", 0)
    num_books = len(OPENING_BOOKS)
    max_visible = 14
    max_scroll = max(0, num_books - max_visible)
    scroll -= event_y * 2
    scroll = max(0, min(scroll, max_scroll))
    draw_book_selector._scroll = scroll


def draw_board_theme_selector(screen, settings):
    screen.fill(constants.THEME["bg"])

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    title = font_big.render("Board Theme", True, constants.THEME["text_title"])
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 50))
    screen.blit(title, tr)

    current = settings.board_theme
    theme_buttons = []

    swatch_size = 30
    gap = 8
    for idx, theme in enumerate(constants.BOARD_THEMES):
        y = 110 + idx * 80
        rect = pygame.Rect(
            constants.WINDOW_WIDTH // 2 - 220, y, 440, 65
        )
        is_active = idx == current
        bg = constants.THEME["btn_accent_fill"] if is_active else constants.THEME["btn_inactive_fill"]
        border = constants.THEME["btn_accent_border"] if is_active else constants.THEME["btn_inactive_border"]
        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)

        colors = theme["colors"]
        light_rect = pygame.Rect(rect.x + 15, rect.y + 12, swatch_size, swatch_size)
        dark_rect = pygame.Rect(rect.x + 15 + swatch_size + gap, rect.y + 12, swatch_size, swatch_size)
        pygame.draw.rect(screen, colors["light"], light_rect)
        pygame.draw.rect(screen, colors["dark"], dark_rect)
        swatch_border = constants.THEME["btn_inactive_border"]
        pygame.draw.rect(screen, swatch_border, light_rect, 1)
        pygame.draw.rect(screen, swatch_border, dark_rect, 1)

        color = constants.THEME["btn_accent_text"] if is_active else constants.THEME["text_bright"]
        lbl = font_mid.render(theme["name"], True, color)
        screen.blit(lbl, (rect.x + 90, rect.y + 20))

        if is_active:
            check = font_mid.render("✔", True, constants.THEME["btn_accent_border"])
            screen.blit(check, (rect.right - 35, rect.y + 18))

        theme_buttons.append((rect, idx))

    back_rect = pygame.Rect(30, 30, 100, 36)
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], back_rect, border_radius=6)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], back_rect, 1, border_radius=6)
    back_text = font_small.render("< Back", True, constants.THEME["btn_back_text"])
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return theme_buttons, back_rect


def handle_board_theme_click(settings, mx, my, theme_buttons, back_rect):
    if back_rect.collidepoint(mx, my):
        return "back", None
    for rect, idx in theme_buttons:
        if rect.collidepoint(mx, my):
            settings.board_theme = idx
            return "select", idx
    return None, None


def draw_piece_style_selector(screen, settings):
    screen.fill(constants.THEME["bg"])

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    title = font_big.render("Piece Style", True, constants.THEME["text_title"])
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 50))
    screen.blit(title, tr)

    current = settings.piece_style
    style_buttons = []

    for idx, (name, _, desc, _) in enumerate(constants.PIECE_STYLES):
        y = 110 + idx * 90
        rect = pygame.Rect(
            constants.WINDOW_WIDTH // 2 - 220, y, 440, 70
        )
        is_active = idx == current
        bg = constants.THEME["btn_accent_fill"] if is_active else constants.THEME["btn_inactive_fill"]
        border = constants.THEME["btn_accent_border"] if is_active else constants.THEME["btn_inactive_border"]
        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)

        color = constants.THEME["btn_accent_text"] if is_active else constants.THEME["text_bright"]
        lbl = font_mid.render(name, True, color)
        screen.blit(lbl, (rect.x + 25, rect.y + 15))

        d = font_small.render(desc, True, constants.THEME["text_dim"] if is_active else constants.THEME["btn_inactive_text_dim"])
        screen.blit(d, (rect.x + 25, rect.y + 42))

        if is_active:
            check = font_mid.render("✔", True, constants.THEME["btn_accent_border"])
            screen.blit(check, (rect.right - 35, rect.y + 22))

        style_buttons.append((rect, idx))

    back_rect = pygame.Rect(30, 30, 100, 36)
    pygame.draw.rect(screen, constants.THEME["btn_back_fill"], back_rect, border_radius=6)
    pygame.draw.rect(screen, constants.THEME["btn_back_border"], back_rect, 1, border_radius=6)
    back_text = font_small.render("< Back", True, constants.THEME["btn_back_text"])
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return style_buttons, back_rect


def handle_piece_style_click(settings, mx, my, style_buttons, back_rect):
    if back_rect.collidepoint(mx, my):
        return "back", None
    for rect, idx in style_buttons:
        if rect.collidepoint(mx, my):
            settings.piece_style = idx
            return "select", idx
    return None, None


def handle_book_click(settings, mx, my, book_buttons, back_rect, dl_rect=None):
    if back_rect and back_rect.collidepoint(mx, my):
        return "back", None
    if dl_rect and dl_rect.collidepoint(mx, my):
        return "download_confirm", None
    for rect, idx in book_buttons:
        if rect.collidepoint(mx, my):
            name, filename, size_str, entries_str, author, url, is_archive = OPENING_BOOKS[idx]
            full = os.path.join(BOOKS_DIR, filename)
            if os.path.exists(full):
                settings.book_name = name
                settings.book_filename = filename
                settings.book_enabled = True
                return "select", filename
            return "pending", idx
    return None, None
