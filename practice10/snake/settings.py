"""
Global constants and configuration for Snake Game.
"""
import pygame

# ── Grid & Display ───────────────────────────────────────────────
CELL_SIZE      = 20          # size of one grid cell in pixels
COLS           = 30          # number of columns in the grid
ROWS           = 25          # number of rows in the grid
WIDTH          = COLS * CELL_SIZE   # window width  (600px)
HEIGHT         = ROWS * CELL_SIZE   # window height (500px)
HUD_HEIGHT     = 40          # extra space at top for score/level display

# ── Game Mechanics ──────────────────────────────────────────────
FOOD_PER_LEVEL = 3           # foods to eat before levelling up
BASE_FPS       = 8           # starting speed (frames per second)
FPS_STEP       = 2           # FPS added each level
MAX_FPS        = 30          # speed cap

# ── Colours ─────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
DARK_GREEN = ( 20,  60,  20)
GREEN      = ( 50, 200,  50)
BRIGHT_GRN = (100, 255, 100)
RED        = (220,  50,  50)
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

# ── Game States ─────────────────────────────────────────────────
STATE_START  = "START"
STATE_RUNNING = "RUNNING"
STATE_PAUSED = "PAUSED"
STATE_DEAD   = "DEAD"

# ── Controls ────────────────────────────────────────────────────
KEY_START    = (pygame.K_SPACE, pygame.K_RETURN)
KEY_PAUSE    = pygame.K_p
KEY_UP       = (pygame.K_UP, pygame.K_w)
KEY_DOWN     = (pygame.K_DOWN, pygame.K_s)
KEY_LEFT     = (pygame.K_LEFT, pygame.K_a)
KEY_RIGHT    = (pygame.K_RIGHT, pygame.K_d)