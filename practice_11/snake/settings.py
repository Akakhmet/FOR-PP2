"""
Global constants and configuration for Snake Game — TSIS 2 Upgrade.
"""
import pygame

# ── Grid & Display ───────────────────────────────────────────────
CELL_SIZE   = 20          # pixel size of one grid cell
COLS        = 30          # grid columns
ROWS        = 25          # grid rows
WIDTH       = COLS * CELL_SIZE    # 600 px
HEIGHT      = ROWS * CELL_SIZE    # 500 px
HUD_HEIGHT  = 40          # top bar for score/level

# ── Gameplay Mechanics ───────────────────────────────────────────
FOOD_PER_LEVEL   = 3      # foods eaten to advance a level
BASE_FPS         = 8      # starting speed (FPS)
FPS_STEP         = 2      # FPS added per level
MAX_FPS          = 30     # speed ceiling
MAX_FOODS        = 3      # max simultaneous food items on board
SPAWN_INTERVAL   = 5.0    # seconds between automatic food spawns

# ── Colours ─────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
DARK_GREEN = ( 20,  60,  20)
GREEN      = ( 50, 200,  50)
BRIGHT_GRN = (100, 255, 100)
WHITE      = (255, 255, 255)
GRAY       = (100, 100, 100)
YELLOW     = (255, 215,   0)
WALL_COLOR = ( 40,  40,  40)
HUD_BG     = ( 15,  15,  15)
GRID_DOT   = ( 18,  18,  18)

# ── Fonts ───────────────────────────────────────────────────────
FONT_HUD   = ("Courier New", 20, True)
FONT_BIG   = ("Courier New", 42, True)
FONT_SMALL = ("Courier New", 22, False)
FONT_TINY  = ("Courier New", 13, False)
FONT_TIMER = ("Courier New", 11, True)

# ── Food Type Definitions ────────────────────────────────────────
# Each food type: name, points (weight), grow segments, color, timer, spawn chance
FOOD_TYPES = [
    {
        "name":   "Normal",
        "points": 10,
        "grow":   1,
        "color":  (220, 50, 50),      # red
        "timer":  None,               # immortal
        "chance": 50,                 # most common
    },
    {
        "name":   "Bonus",
        "points": 30,
        "grow":   1,
        "color":  (255, 165, 0),      # orange
        "timer":  8.0,
        "chance": 25,
    },
    {
        "name":   "Rare",
        "points": 60,
        "grow":   2,
        "color":  (180, 0, 220),      # purple
        "timer":  5.0,
        "chance": 15,
    },
    {
        "name":   "Golden",
        "points": 100,
        "grow":   3,
        "color":  (255, 215, 0),      # gold
        "timer":  3.0,
        "chance": 10,                 # rarest
    },
]

# Build weighted pool for random.choice() — higher chance = more entries
FOOD_POOL = []
for ft in FOOD_TYPES:
    FOOD_POOL.extend([ft] * ft["chance"])

# ── Game States ─────────────────────────────────────────────────
STATE_START   = "START"
STATE_RUNNING = "RUNNING"
STATE_PAUSED  = "PAUSED"
STATE_DEAD    = "DEAD"

# ── Controls ────────────────────────────────────────────────────
KEY_START    = (pygame.K_SPACE, pygame.K_RETURN)
KEY_PAUSE    = pygame.K_p
KEY_UP       = (pygame.K_UP, pygame.K_w)
KEY_DOWN     = (pygame.K_DOWN, pygame.K_s)
KEY_LEFT     = (pygame.K_LEFT, pygame.K_a)
KEY_RIGHT    = (pygame.K_RIGHT, pygame.K_d)