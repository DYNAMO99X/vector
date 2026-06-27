import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PIECES_DIR = os.path.join(ASSETS_DIR, "pieces")

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 720
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
MARGIN_LEFT = 40
MARGIN_TOP = 40
PANEL_WIDTH = WINDOW_WIDTH - BOARD_SIZE - MARGIN_LEFT * 2
PANEL_X = MARGIN_LEFT + BOARD_SIZE + 20
FPS = 60

LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
SELECTED_SQUARE = (246, 246, 105)
LEGAL_MOVE_DOT = (0, 0, 0, 80)
LEGAL_CAPTURE_RING = (0, 0, 0, 80)
LAST_MOVE_SQUARE = (205, 210, 106)
CHECK_SQUARE = (235, 97, 80)

BG_COLOR = (49, 46, 43)
PANEL_BG = (39, 37, 34)
PANEL_BORDER = (70, 67, 63)
TEXT_COLOR = (210, 210, 210)
TEXT_DIM = (150, 150, 150)
COORD_COLOR = (200, 200, 200)

BOARD_THEMES = [
    {
        "name": "Classic",
        "colors": {
            "light": (238, 238, 210),
            "dark": (118, 150, 86),
            "selected": (246, 246, 105),
            "last_move": (205, 210, 106),
            "check": (235, 97, 80),
        },
    },
    {
        "name": "Marble",
        "colors": {
            "light": (230, 225, 215),
            "dark": (160, 150, 130),
            "selected": (240, 230, 140),
            "last_move": (200, 195, 160),
            "check": (220, 100, 80),
        },
    },
    {
        "name": "Ocean",
        "colors": {
            "light": (220, 230, 240),
            "dark": (95, 135, 175),
            "selected": (230, 240, 140),
            "last_move": (160, 190, 210),
            "check": (230, 95, 80),
        },
    },
    {
        "name": "Walnut",
        "colors": {
            "light": (225, 200, 170),
            "dark": (155, 115, 70),
            "selected": (240, 220, 120),
            "last_move": (190, 165, 130),
            "check": (220, 90, 75),
        },
    },
    {
        "name": "Emerald",
        "colors": {
            "light": (210, 225, 200),
            "dark": (60, 140, 100),
            "selected": (230, 240, 100),
            "last_move": (160, 200, 150),
            "check": (230, 90, 75),
        },
    },
    {
        "name": "Midnight",
        "colors": {
            "light": (110, 110, 130),
            "dark": (55, 55, 75),
            "selected": (160, 160, 80),
            "last_move": (90, 95, 110),
            "check": (180, 65, 65),
        },
    },
]

PIECE_STYLES = [
    ("Unicode", None, "Font-based, always available", 1.0),
    ("Merida", "merida", "Shaded pieces, used by Lichess", 0.8),
    ("Julius", "julius", "Clean redesign of Merida", 0.8),
    ("Alpha", "alpha", "Minimalist silhouette style", 0.80),
]

PIECE_NAMES = {
    "P": "P", "N": "N", "B": "B", "R": "R", "Q": "Q", "K": "K",
}

DARK = {
    "bg": (49, 46, 43),
    "panel_bg": (39, 37, 34),
    "panel_border": (70, 67, 63),
    "text": (210, 210, 210),
    "text_dim": (150, 150, 150),
    "text_title": (220, 220, 220),
    "text_bright": (245, 245, 245),
    "thinking_text": (160, 160, 160),
    "overlay": (0, 0, 0),
    "display_bg": (30, 30, 30),
    "btn_back_fill": (65, 65, 65),
    "btn_back_border": (100, 100, 100),
    "btn_back_text": (180, 180, 180),
    "btn_accent_fill": (50, 70, 65),
    "btn_accent_border": (80, 160, 130),
    "btn_accent_text": (140, 230, 200),
    "btn_danger_fill": (80, 50, 50),
    "btn_danger_border": (120, 70, 70),
    "btn_danger_text": (200, 140, 140),
    "btn_inactive_fill": (45, 45, 45),
    "btn_inactive_border": (70, 70, 70),
    "btn_inactive_text": (180, 180, 180),
    "btn_inactive_text_dim": (120, 120, 120),
    "btn_row_fill": (55, 55, 55),
    "btn_row_border": (90, 90, 90),
    "btn_row_text": (220, 220, 220),
    "btn_row_text_dim": (150, 150, 150),
    "move_well_bg": (30, 28, 25),
    "scroll_bg": (50, 48, 45),
    "scroll_thumb": (120, 120, 120),
}

LIGHT = {
    "bg": (235, 228, 218),
    "panel_bg": (250, 245, 238),
    "panel_border": (190, 182, 172),
    "text": (40, 38, 35),
    "text_dim": (130, 125, 118),
    "text_title": (60, 55, 48),
    "text_bright": (30, 28, 25),
    "thinking_text": (160, 160, 160),
    "overlay": (255, 255, 255),
    "display_bg": (220, 215, 208),
    "btn_back_fill": (210, 204, 196),
    "btn_back_border": (170, 165, 158),
    "btn_back_text": (70, 66, 60),
    "btn_accent_fill": (60, 190, 155),
    "btn_accent_border": (40, 160, 130),
    "btn_accent_text": (255, 255, 255),
    "btn_danger_fill": (220, 180, 180),
    "btn_danger_border": (180, 100, 100),
    "btn_danger_text": (100, 30, 30),
    "btn_inactive_fill": (200, 195, 188),
    "btn_inactive_border": (165, 160, 154),
    "btn_inactive_text": (130, 126, 120),
    "btn_inactive_text_dim": (100, 96, 90),
    "btn_row_fill": (215, 210, 202),
    "btn_row_border": (175, 170, 164),
    "btn_row_text": (50, 48, 44),
    "btn_row_text_dim": (120, 116, 110),
    "move_well_bg": (220, 215, 208),
    "scroll_bg": (200, 195, 188),
    "scroll_thumb": (160, 155, 148),
}

THEME = DARK


def set_theme(mode):
    global THEME
    if mode == "light":
        THEME = LIGHT
    else:
        THEME = DARK


SCREEN_TITLE = "VECTOR — Vibe-Engineered Chess Tactician for Online Rankings"

UNICODE_PIECES = {
    "wK": "\u2654", "wQ": "\u2655", "wR": "\u2656",
    "wB": "\u2657", "wN": "\u2658", "wP": "\u2659",
    "bK": "\u265A", "bQ": "\u265B", "bR": "\u265C",
    "bB": "\u265D", "bN": "\u265E", "bP": "\u265F",
}
