from __future__ import annotations

BOARD_SIZE = 4
WINNING_TILE = 2048

WINDOW_BG = "#faf8ef"
GRID_BG = "#bbada0"
EMPTY_TILE_BG = "#cdc1b4"
DARK_TEXT = "#776e65"
LIGHT_TEXT = "#f9f6f2"
BUTTON_BG = "#8f7a66"
BUTTON_ACTIVE_BG = "#9f8b77"
WHITE = "#ffffff"

TILE_COLORS: dict[int, str] = {
    0: EMPTY_TILE_BG,
    2: "#eee4da",
    4: "#ede0c8",
    8: "#f2b179",
    16: "#f59563",
    32: "#f67c5f",
    64: "#f65e3b",
    128: "#edcf72",
    256: "#edcc61",
    512: "#edc850",
    1024: "#edc53f",
    2048: "#edc22e",
    4096: "#3c3a32",
    8192: "#3c3a32",
}

TILE_TEXT_COLORS: dict[int, str] = {
    0: DARK_TEXT,
    2: DARK_TEXT,
    4: DARK_TEXT,
    8: LIGHT_TEXT,
    16: LIGHT_TEXT,
    32: LIGHT_TEXT,
    64: LIGHT_TEXT,
    128: LIGHT_TEXT,
    256: LIGHT_TEXT,
    512: LIGHT_TEXT,
    1024: LIGHT_TEXT,
    2048: LIGHT_TEXT,
    4096: LIGHT_TEXT,
    8192: LIGHT_TEXT,
}

TILE_FONT_SIZES: dict[int, int] = {
    2: 34,
    4: 34,
    8: 34,
    16: 32,
    32: 32,
    64: 32,
    128: 28,
    256: 28,
    512: 28,
    1024: 23,
    2048: 23,
    4096: 20,
    8192: 20,
}

CELL_SIZE = 108
CELL_GAP = 12
BOARD_PIXELS = BOARD_SIZE * CELL_SIZE + (BOARD_SIZE + 1) * CELL_GAP
ANIMATION_STEPS = (0.72, 0.84, 0.94, 1.06, 1.0)
ANIMATION_DELAY_MS = 22
