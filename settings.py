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
]

DEPTH_PRESETS = [2, 3, 4, 5, 6, 8, 10]


class GameSettings:
    def __init__(self):
        self.time_minutes = 10
        self.time_increment = 0
        self.bot_version = 0
        self.bot_depth = 3

    def reset(self):
        self.time_minutes = 10
        self.time_increment = 0
        self.bot_version = 0
        self.bot_depth = 3

    def total_seconds(self):
        return self.time_minutes * 60


def draw_main_menu(screen):
    screen.fill(constants.BG_COLOR)

    font_big = pygame.font.SysFont("Segoe UI", 48, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    title = font_big.render("VECTOR", True, (230, 230, 230))
    title_rect = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 180))
    screen.blit(title, title_rect)

    glow = font_big.render("VECTOR", True, (60, 180, 200))
    for dx, dy in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
        screen.blit(glow, (title_rect.x + dx, title_rect.y + dy))
    screen.blit(title, title_rect)

    subtitle = font_small.render(
        "Vibe-Engineered Chess Tactician for Online Rankings",
        True, constants.TEXT_DIM
    )
    sr = subtitle.get_rect(center=(constants.WINDOW_WIDTH // 2, 225))
    screen.blit(subtitle, sr)

    button_w = 220
    button_h = 55
    btn_x = constants.WINDOW_WIDTH // 2 - button_w // 2

    play_rect = pygame.Rect(btn_x, 310, button_w, button_h)
    pygame.draw.rect(screen, (50, 70, 65), play_rect, border_radius=10)
    pygame.draw.rect(screen, (80, 160, 130), play_rect, 2, border_radius=10)
    play_text = font_mid.render("Play", True, (140, 230, 200))
    pt_rect = play_text.get_rect(center=play_rect.center)
    screen.blit(play_text, pt_rect)

    settings_rect = pygame.Rect(btn_x, 385, button_w, button_h)
    pygame.draw.rect(screen, (65, 65, 65), settings_rect, border_radius=10)
    pygame.draw.rect(screen, (120, 120, 120), settings_rect, 2, border_radius=10)
    stext = font_mid.render("Settings", True, (190, 190, 190))
    st_rect = stext.get_rect(center=settings_rect.center)
    screen.blit(stext, st_rect)

    return play_rect, settings_rect


def draw_settings_list(screen, settings):
    screen.fill(constants.BG_COLOR)

    font_big = pygame.font.SysFont("Segoe UI", 32, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 18)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    title = font_big.render("Settings", True, (220, 220, 220))
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 80))
    screen.blit(title, tr)

    items = [
        ("Match Time", "Set game timer and increment", True),
        ("Bot Version", f"Currently: {BOT_VERSIONS[settings.bot_version][0]}", True),
        ("Bot Depth", f"Search depth: {settings.bot_depth}", True),
        ("Board Theme", "Customize colors", False),
    ]

    buttons = []
    start_y = 160
    for i, (label, desc, enabled) in enumerate(items):
        y = start_y + i * 90
        rect = pygame.Rect(
            constants.WINDOW_WIDTH // 2 - 200, y, 400, 70
        )
        color = (55, 55, 55) if enabled else (45, 45, 45)
        border = (90, 90, 90) if enabled else (60, 60, 60)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 2, border_radius=8)

        text_color = (220, 220, 220) if enabled else (120, 120, 120)
        lbl = font_mid.render(label, True, text_color)
        screen.blit(lbl, (rect.x + 20, rect.y + 15))

        d = font_small.render(desc, True, (150, 150, 150) if enabled else (90, 90, 90))
        screen.blit(d, (rect.x + 20, rect.y + 40))

        if enabled:
            arrow = font_mid.render(">", True, (100, 180, 160))
            screen.blit(arrow, (rect.right - 25, rect.y + 22))

        buttons.append((rect, label, enabled))

    back_rect = pygame.Rect(30, 30, 100, 36)
    pygame.draw.rect(screen, (65, 65, 65), back_rect, border_radius=6)
    pygame.draw.rect(screen, (100, 100, 100), back_rect, 1, border_radius=6)
    back_text = font_mid.render("< Back", True, (180, 180, 180))
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return buttons, back_rect


def draw_time_selector(screen, settings):
    screen.fill(constants.BG_COLOR)

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_button = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 14)
    font_clock = pygame.font.SysFont("Segoe UI", 72, bold=True)

    title = font_big.render("Time Control", True, (220, 220, 220))
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 50))
    screen.blit(title, tr)

    time_display = pygame.Rect(
        constants.WINDOW_WIDTH // 2 - 150, 80, 300, 110
    )
    pygame.draw.rect(screen, (30, 30, 30), time_display, border_radius=12)
    pygame.draw.rect(screen, (80, 160, 130), time_display, 2, border_radius=12)

    time_str = f"{settings.time_minutes:02d} : {settings.time_increment:02d}"
    clock_text = font_clock.render(time_str, True, (140, 220, 180))
    ct_rect = clock_text.get_rect(center=(time_display.centerx - 3, time_display.centery - 16))
    screen.blit(clock_text, ct_rect)

    label_m = font_small.render("Minutes", True, (160, 200, 180))
    screen.blit(label_m, (time_display.centerx - 78, time_display.bottom - 28))
    label_i = font_small.render("Increment", True, (160, 200, 180))
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
        bg = (50, 70, 65) if is_active else (50, 50, 50)
        border = (80, 160, 130) if is_active else (80, 80, 80)
        pygame.draw.rect(screen, bg, rect, border_radius=6)
        pygame.draw.rect(screen, border, rect, 2, border_radius=6)
        text = font_button.render(label, True,
                                   (140, 230, 200) if is_active else (180, 180, 180))
        t_rect = text.get_rect(center=rect.center)
        screen.blit(text, t_rect)
        preset_buttons.append((rect, mins, inc))

    adjust_y = start_y + 2 * (ph + gap) + 20

    adjust_font = pygame.font.SysFont("Segoe UI", 14, bold=True)

    controls = []
    mins_title = font_small.render("Minutes", True, constants.TEXT_COLOR)
    screen.blit(mins_title, (constants.WINDOW_WIDTH // 2 - 160, adjust_y))

    mins_controls = []
    for val, label in [(-5, "-5"), (-1, "-1"), (1, "+1"), (5, "+5")]:
        bx = constants.WINDOW_WIDTH // 2 - 160 + (list.index([-5, -1, 1, 5], val)) * 80
        by = adjust_y + 22
        rect = pygame.Rect(bx, by, 70, 32)
        pygame.draw.rect(screen, (55, 55, 55), rect, border_radius=6)
        pygame.draw.rect(screen, (80, 80, 80), rect, 1, border_radius=6)
        text = adjust_font.render(label, True, (200, 200, 200))
        t_rect = text.get_rect(center=rect.center)
        screen.blit(text, t_rect)
        mins_controls.append((rect, "minutes", val))

    inc_y = adjust_y + 65
    inc_title = font_small.render("Increment (sec)", True, constants.TEXT_COLOR)
    screen.blit(inc_title, (constants.WINDOW_WIDTH // 2 - 160, inc_y))

    inc_controls = []
    for val, label in [(-1, "-1"), (1, "+1")]:
        bx = constants.WINDOW_WIDTH // 2 - 80 + list.index([-1, 1], val) * 90
        by = inc_y + 22
        rect = pygame.Rect(bx, by, 70, 32)
        pygame.draw.rect(screen, (55, 55, 55), rect, border_radius=6)
        pygame.draw.rect(screen, (80, 80, 80), rect, 1, border_radius=6)
        text = adjust_font.render(label, True, (200, 200, 200))
        t_rect = text.get_rect(center=rect.center)
        screen.blit(text, t_rect)
        inc_controls.append((rect, "increment", val))

    btn_y = constants.WINDOW_HEIGHT - 70

    save_rect = pygame.Rect(
        constants.WINDOW_WIDTH // 2 - 110, btn_y, 100, 42
    )
    pygame.draw.rect(screen, (50, 70, 65), save_rect, border_radius=8)
    pygame.draw.rect(screen, (80, 160, 130), save_rect, 2, border_radius=8)
    save_text = font_mid.render("Save", True, (140, 230, 200))
    st_rect = save_text.get_rect(center=save_rect.center)
    screen.blit(save_text, st_rect)

    back_btn_rect = pygame.Rect(
        constants.WINDOW_WIDTH // 2 + 20, btn_y, 100, 42
    )
    pygame.draw.rect(screen, (65, 65, 65), back_btn_rect, border_radius=8)
    pygame.draw.rect(screen, (100, 100, 100), back_btn_rect, 2, border_radius=8)
    back_text = font_mid.render("Back", True, (180, 180, 180))
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
    screen.fill(constants.BG_COLOR)

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    title = font_big.render("Bot Version", True, (220, 220, 220))
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
        bg = (50, 70, 65) if is_active else (45, 45, 45)
        border = (80, 160, 130) if is_active else (70, 70, 70)
        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)

        color = (140, 230, 200) if is_active else (200, 200, 200)
        lbl = font_mid.render(name, True, color)
        screen.blit(lbl, (rect.x + 25, rect.y + 18))

        d = font_small.render(desc, True, (160, 160, 160) if is_active else (120, 120, 120))
        screen.blit(d, (rect.x + 25, rect.y + 50))

        if is_active:
            check = font_mid.render("✔", True, (80, 200, 150))
            screen.blit(check, (rect.right - 35, rect.y + 28))

        version_buttons.append((rect, idx))

    back_rect = pygame.Rect(30, 30, 100, 36)
    pygame.draw.rect(screen, (65, 65, 65), back_rect, border_radius=6)
    pygame.draw.rect(screen, (100, 100, 100), back_rect, 1, border_radius=6)
    back_text = font_small.render("< Back", True, (180, 180, 180))
    bt_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, bt_rect)

    return version_buttons, back_rect


def draw_bot_depth_selector(screen, settings):
    screen.fill(constants.BG_COLOR)

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_mid = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_button = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 14)
    font_display = pygame.font.SysFont("Segoe UI", 72, bold=True)

    title = font_big.render("Bot Depth", True, (220, 220, 220))
    tr = title.get_rect(center=(constants.WINDOW_WIDTH // 2, 50))
    screen.blit(title, tr)

    depth_display = pygame.Rect(
        constants.WINDOW_WIDTH // 2 - 150, 80, 300, 110
    )
    pygame.draw.rect(screen, (30, 30, 30), depth_display, border_radius=12)
    pygame.draw.rect(screen, (80, 160, 130), depth_display, 2, border_radius=12)

    depth_text = font_display.render(str(settings.bot_depth), True, (140, 220, 180))
    dt_rect = depth_text.get_rect(center=(depth_display.centerx, depth_display.centery - 10))
    screen.blit(depth_text, dt_rect)

    label_d = font_small.render("Ply depth", True, (160, 200, 180))
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
        bg = (50, 70, 65) if is_active else (50, 50, 50)
        border = (80, 160, 130) if is_active else (80, 80, 80)
        pygame.draw.rect(screen, bg, rect, border_radius=6)
        pygame.draw.rect(screen, border, rect, 2, border_radius=6)
        text = font_button.render(str(d), True,
                                   (140, 230, 200) if is_active else (180, 180, 180))
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
        pygame.draw.rect(screen, (55, 55, 55), rect, border_radius=6)
        pygame.draw.rect(screen, (80, 80, 80), rect, 1, border_radius=6)
        text = adjust_font.render(label, True, (200, 200, 200))
        t_rect = text.get_rect(center=rect.center)
        screen.blit(text, t_rect)
        depth_controls.append((rect, val))

    btn_y = constants.WINDOW_HEIGHT - 70

    save_rect = pygame.Rect(
        constants.WINDOW_WIDTH // 2 - 110, btn_y, 100, 42
    )
    pygame.draw.rect(screen, (50, 70, 65), save_rect, border_radius=8)
    pygame.draw.rect(screen, (80, 160, 130), save_rect, 2, border_radius=8)
    save_text = font_mid.render("Save", True, (140, 230, 200))
    st_rect = save_text.get_rect(center=save_rect.center)
    screen.blit(save_text, st_rect)

    back_btn_rect = pygame.Rect(
        constants.WINDOW_WIDTH // 2 + 20, btn_y, 100, 42
    )
    pygame.draw.rect(screen, (65, 65, 65), back_btn_rect, border_radius=8)
    pygame.draw.rect(screen, (100, 100, 100), back_btn_rect, 2, border_radius=8)
    back_text = font_mid.render("Back", True, (180, 180, 180))
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
