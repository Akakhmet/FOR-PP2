"""
Snake Game — Pygame Extended Version
=====================================
Features:
  1. Wall (border) collision detection
  2. Random food placement (avoids walls and snake body)
  3. Levels system (every FOOD_PER_LEVEL foods eaten → next level)
  4. Speed increases each level
  5. Score and level counter displayed on screen
  6. Code is fully commented
"""

import pygame
import random
import sys

# ── Initialize Pygame ─────────────────────────────────────────────
pygame.init()

# ── Constants ────────────────────────────────────────────────────
CELL_SIZE      = 20          # size of one grid cell in pixels
COLS           = 30          # number of columns in the grid
ROWS           = 25          # number of rows in the grid
WIDTH          = COLS * CELL_SIZE   # window width  (600px)
HEIGHT         = ROWS * CELL_SIZE   # window height (500px)
HUD_HEIGHT     = 40          # extra space at top for score/level display

FOOD_PER_LEVEL = 3           # foods to eat before levelling up
BASE_FPS       = 8           # starting speed (frames per second)
FPS_STEP       = 2           # FPS added each level
MAX_FPS        = 30          # speed cap

# ── Colours ──────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
DARK_GREEN = ( 20,  60,  20)
GREEN      = ( 50, 200,  50)
BRIGHT_GRN = (100, 255, 100)
RED        = (220,  50,  50)
WHITE      = (255, 255, 255)
GRAY       = (100, 100, 100)
YELLOW     = (255, 215,   0)
WALL_COLOR = ( 40,  40,  40)

# ── Display setup ────────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT + HUD_HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

# ── Fonts ────────────────────────────────────────────────────────
font_hud   = pygame.font.SysFont("Courier New", 20, bold=True)
font_big   = pygame.font.SysFont("Courier New", 42, bold=True)
font_small = pygame.font.SysFont("Courier New", 22)


# ─────────────────────────────────────────────────────────────────
# Helper: draw a single grid cell
# ─────────────────────────────────────────────────────────────────
def draw_cell(surface, col, row, color, margin=1):
    """Draw a filled rectangle for one grid cell with an optional margin."""
    rect = pygame.Rect(
        col * CELL_SIZE + margin,
        row * CELL_SIZE + margin + HUD_HEIGHT,
        CELL_SIZE - margin * 2,
        CELL_SIZE - margin * 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=3)


# ─────────────────────────────────────────────────────────────────
# Helper: draw the border walls
# ─────────────────────────────────────────────────────────────────
def draw_walls(surface):
    """
    Draw the outer wall ring around the playable area.
    The wall occupies column 0, column COLS-1, row 0, and row ROWS-1.
    """
    for col in range(COLS):
        draw_cell(surface, col, 0,        WALL_COLOR, margin=0)   # top row
        draw_cell(surface, col, ROWS - 1, WALL_COLOR, margin=0)   # bottom row
    for row in range(1, ROWS - 1):
        draw_cell(surface, 0,        row, WALL_COLOR, margin=0)   # left col
        draw_cell(surface, COLS - 1, row, WALL_COLOR, margin=0)   # right col


# ─────────────────────────────────────────────────────────────────
# Helper: draw HUD (score, level, speed)
# ─────────────────────────────────────────────────────────────────
def draw_hud(surface, score, level, fps):
    """Render score, level, and current speed in the top bar."""
    # Background bar
    pygame.draw.rect(surface, (15, 15, 15), (0, 0, WIDTH, HUD_HEIGHT))
    pygame.draw.line(surface, DARK_GREEN, (0, HUD_HEIGHT - 1), (WIDTH, HUD_HEIGHT - 1), 1)

    score_surf = font_hud.render(f"SCORE: {score}", True, GREEN)
    level_surf = font_hud.render(f"LEVEL: {level}", True, YELLOW)
    speed_surf = font_hud.render(f"SPEED: {fps} FPS", True, GRAY)

    surface.blit(score_surf, (14, 10))
    surface.blit(level_surf, (WIDTH // 2 - level_surf.get_width() // 2, 10))
    surface.blit(speed_surf, (WIDTH - speed_surf.get_width() - 14, 10))


# ─────────────────────────────────────────────────────────────────
# Helper: random food position
# ─────────────────────────────────────────────────────────────────
def random_food(snake_body):
    """
    Choose a random grid cell for the food that:
      - Is NOT on the wall border (row/col 0 or max)
      - Is NOT occupied by any snake segment
    Retries until a valid cell is found.
    """
    snake_set = set(snake_body)   # O(1) lookup
    while True:
        col = random.randint(1, COLS - 2)   # 1 .. COLS-2 (inside walls)
        row = random.randint(1, ROWS - 2)   # 1 .. ROWS-2
        if (col, row) not in snake_set:
            return (col, row)


# ─────────────────────────────────────────────────────────────────
# Helper: centered text overlay
# ─────────────────────────────────────────────────────────────────
def draw_overlay(surface, title, subtitle=""):
    """Draw a semi-transparent overlay with a title and subtitle."""
    overlay = pygame.Surface((WIDTH, HEIGHT + HUD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    title_surf = font_big.render(title, True, GREEN)
    surface.blit(title_surf, (
        WIDTH // 2 - title_surf.get_width() // 2,
        (HEIGHT + HUD_HEIGHT) // 2 - 50,
    ))

    if subtitle:
        sub_surf = font_small.render(subtitle, True, WHITE)
        surface.blit(sub_surf, (
            WIDTH // 2 - sub_surf.get_width() // 2,
            (HEIGHT + HUD_HEIGHT) // 2 + 10,
        ))


# ─────────────────────────────────────────────────────────────────
# Main game function
# ─────────────────────────────────────────────────────────────────
def main():
    # ── Game state variables ──────────────────────────────────────
    # Snake is a list of (col, row) tuples; index 0 = head
    snake      = [(COLS // 2, ROWS // 2),
                  (COLS // 2 - 1, ROWS // 2),
                  (COLS // 2 - 2, ROWS // 2)]

    direction  = (1, 0)        # current movement direction (dx, dy)
    next_dir   = (1, 0)        # buffered next direction (applied each frame)

    food       = random_food(snake)

    score      = 0
    level      = 1
    food_eaten = 0             # counter resets each level
    current_fps = BASE_FPS     # current game speed

    state      = "START"       # game states: START | RUNNING | PAUSED | DEAD

    # ── Main loop ─────────────────────────────────────────────────
    while True:

        # ── Event handling ────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                # Start / restart / unpause on SPACE or ENTER
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if state in ("START", "DEAD"):
                        # Full reset
                        snake       = [(COLS // 2, ROWS // 2),
                                       (COLS // 2 - 1, ROWS // 2),
                                       (COLS // 2 - 2, ROWS // 2)]
                        direction   = (1, 0)
                        next_dir    = (1, 0)
                        food        = random_food(snake)
                        score       = 0
                        level       = 1
                        food_eaten  = 0
                        current_fps = BASE_FPS
                        state       = "RUNNING"
                    elif state == "PAUSED":
                        state = "RUNNING"

                # Pause / unpause on P
                elif event.key == pygame.K_p:
                    if state == "RUNNING":
                        state = "PAUSED"
                    elif state == "PAUSED":
                        state = "RUNNING"

                # ── Direction input (Arrow keys + WASD) ──────────
                # Rule: cannot reverse direction 180° in one move
                elif event.key in (pygame.K_UP, pygame.K_w):
                    if direction != (0, 1):     # not currently moving down
                        next_dir = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if direction != (0, -1):    # not currently moving up
                        next_dir = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if direction != (1, 0):     # not currently moving right
                        next_dir = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if direction != (-1, 0):    # not currently moving left
                        next_dir = (1, 0)

        # ── Game logic (only when RUNNING) ───────────────────────
        if state == "RUNNING":

            # Apply buffered direction
            direction = next_dir

            # Calculate new head position
            head     = snake[0]
            new_head = (head[0] + direction[0], head[1] + direction[1])

            # ── 1. Wall collision check ───────────────────────────
            # If head lands on the outer border → game over
            col, row = new_head
            if col <= 0 or col >= COLS - 1 or row <= 0 or row >= ROWS - 1:
                state = "DEAD"

            # ── 2. Self-collision check ───────────────────────────
            elif new_head in snake:
                state = "DEAD"

            else:
                # Move snake: insert new head at front
                snake.insert(0, new_head)

                # ── 3. Food check ─────────────────────────────────
                if new_head == food:
                    # Snake grows: do NOT pop the tail
                    food_eaten += 1
                    score      += 10 * level   # bonus scales with level

                    # ── 4. Level-up check ─────────────────────────
                    if food_eaten >= FOOD_PER_LEVEL:
                        level      += 1
                        food_eaten  = 0
                        # Increase speed, but cap at MAX_FPS
                        current_fps = min(MAX_FPS, BASE_FPS + (level - 1) * FPS_STEP)

                    # Place new food (avoids walls and the now-longer snake)
                    food = random_food(snake)

                else:
                    # No food eaten: remove tail so snake stays same length
                    snake.pop()

        # ── Drawing ───────────────────────────────────────────────
        screen.fill(BLACK)

        # Background grid dots
        for c in range(1, COLS - 1):
            for r in range(1, ROWS - 1):
                pygame.draw.rect(
                    screen, (18, 18, 18),
                    (c * CELL_SIZE + CELL_SIZE // 2 - 1,
                     r * CELL_SIZE + CELL_SIZE // 2 - 1 + HUD_HEIGHT,
                     2, 2)
                )

        # Walls
        draw_walls(screen)

        # Food — bright red circle
        food_cx = food[0] * CELL_SIZE + CELL_SIZE // 2
        food_cy = food[1] * CELL_SIZE + CELL_SIZE // 2 + HUD_HEIGHT
        pygame.draw.circle(screen, RED, (food_cx, food_cy), CELL_SIZE // 2 - 2)
        # Highlight dot on food
        pygame.draw.circle(screen, (255, 150, 150),
                           (food_cx - 3, food_cy - 3), 3)

        # Snake segments
        for idx, (c, r) in enumerate(snake):
            if idx == 0:
                # Head — brightest colour
                color = BRIGHT_GRN
            else:
                # Body — gradually darker toward tail
                fade  = max(0, 1.0 - idx / len(snake) * 0.75)
                color = (int(50 * fade), int(200 * fade), int(50 * fade))
            draw_cell(screen, c, r, color)

        # HUD
        draw_hud(screen, score, level, current_fps)

        # ── State overlays ────────────────────────────────────────
        if state == "START":
            draw_overlay(screen, "SNAKE",
                         "Press SPACE or ENTER to start  |  WASD / Arrows")

        elif state == "PAUSED":
            draw_overlay(screen, "PAUSED", "Press P or SPACE to resume")

        elif state == "DEAD":
            draw_overlay(screen,
                         "GAME OVER",
                         f"Score: {score}   Level: {level}   |   SPACE to restart")

        # ── Tick ──────────────────────────────────────────────────
        pygame.display.flip()
        clock.tick(current_fps)   # control speed via FPS cap


# ── Entry point ──────────────────────────────────────────────────
if __name__ == "__main__":
    main()