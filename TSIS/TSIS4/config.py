# config.py — shared constants for TSIS 4 Snake

# ── Database ──────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "snakegame",
    "user":     "postgres",
    "password": "080302",
}

# ── Grid & Window ─────────────────────────────────────────────────
CELL = 20          # pixels per grid cell
COLS = 24          # grid columns
ROWS = 24          # grid rows
HUD_H = 70         # HUD strip at the top (pixels)

SW = COLS * CELL            # 480
SH = ROWS * CELL + HUD_H   # 550

# ── Snake speed (steps per second) ────────────────────────────────
SPEED_BASE  = 7    # steps/s at level 1
SPEED_STEP  = 1    # added per level
SPEED_MAX   = 16
SPEED_BOOST = 5    # extra steps/s for nitro
SPEED_SLOW  = -3   # reduction for slow-mo (floored at 3)

# ── Level progression ─────────────────────────────────────────────
FOODS_PER_LEVEL = 5    # food eaten to level up
OBS_START_LEVEL = 3    # obstacles appear from this level
OBS_PER_LEVEL   = 3    # new obstacles per level

# ── Colors ────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (120, 120, 120)
DARK       = (30,  30,  50)
BG         = (18,  18,  30)
GRID_COLOR = (30,  30,  48)
WALL_COLOR = (80,  80,  100)

FOOD_NORMAL = (220, 200, 0)
FOOD_BONUS  = (255, 120, 0)
FOOD_HEAVY  = (150, 220, 100)
POISON_COL  = (140, 0,   20)

PU_SPEED    = (255, 60,  60)
PU_SLOW     = (60,  100, 255)
PU_SHIELD   = (220, 220, 50)

SNAKE_DEFAULT = (40, 180, 40)
HEAD_DEFAULT  = (80, 230, 80)
