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

PIECE_NAMES = {
    "P": "P", "N": "N", "B": "B", "R": "R", "Q": "Q", "K": "K",
}

SCREEN_TITLE = "VECTOR — Vibe-Engineered Chess Tactician for Online Rankings"

UNICODE_PIECES = {
    "wK": "\u2654", "wQ": "\u2655", "wR": "\u2656",
    "wB": "\u2657", "wN": "\u2658", "wP": "\u2659",
    "bK": "\u265A", "bQ": "\u265B", "bR": "\u265C",
    "bB": "\u265D", "bN": "\u265E", "bP": "\u265F",
}
