"""
Snake Game — Pygame Extended Version (TSIS 2 Upgrade)
======================================================
New features added on top of Practice 8:
  1. Randomly generating food with different weights (points & grow amount)
  2. Foods disappear after a countdown timer
  3. Multiple food items on the board simultaneously
  4. Code is fully commented
"""

import pygame
import random
import sys

# ── Initialize Pygame ─────────────────────────────────────────────
pygame.init()

# ── Grid & window constants ───────────────────────────────────────
CELL_SIZE   = 20          # pixel size of one grid cell
COLS        = 30          # grid columns
ROWS        = 25          # grid rows
WIDTH       = COLS * CELL_SIZE    # 600 px
HEIGHT      = ROWS * CELL_SIZE    # 500 px
HUD_HEIGHT  = 40          # top bar for score / level

# ── Gameplay constants ────────────────────────────────────────────
FOOD_PER_LEVEL   = 3      # foods eaten to advance a level
BASE_FPS         = 8      # starting speed (FPS)
FPS_STEP         = 2      # FPS added per level
MAX_FPS          = 30     # speed ceiling
MAX_FOODS        = 3      # maximum simultaneous food items on board
SPAWN_INTERVAL   = 5.0    # seconds between automatic new food spawns

# ── Colours ──────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
DARK_GREEN = ( 20,  60,  20)
GREEN      = ( 50, 200,  50)
BRIGHT_GRN = (100, 255, 100)
WHITE      = (255, 255, 255)
GRAY       = (100, 100, 100)
YELLOW     = (255, 215,   0)
WALL_COLOR = ( 40,  40,  40)

# ── Food type definitions ─────────────────────────────────────────
# Each food type is a dict with:
#   name    – display label shown in the legend
#   points  – score awarded when eaten  (this is the "weight" / value)
#   grow    – tail segments added (1 = normal, 2 = double, etc.)
#   color   – RGB colour of the circle on the board
#   timer   – seconds before the food disappears (None = immortal)
#   chance  – relative spawn probability weight (higher = more common)
FOOD_TYPES = [
    {
        "name":   "Normal",
        "points": 10,        # low value
        "grow":   1,         # grow 1 segment
        "color":  (220, 50,  50),   # red
        "timer":  None,      # never disappears
        "chance": 50,        # most common
    },
    {
        "name":   "Bonus",
        "points": 30,        # medium value
        "grow":   1,
        "color":  (255, 165,  0),   # orange
        "timer":  8.0,       # disappears after 8 seconds
        "chance": 25,
    },
    {
        "name":   "Rare",
        "points": 60,        # high value
        "grow":   2,         # grow 2 segments
        "color":  (180,  0, 220),   # purple
        "timer":  5.0,       # disappears quickly
        "chance": 15,
    },
    {
        "name":   "Golden",
        "points": 100,       # jackpot value
        "grow":   3,         # grow 3 segments
        "color":  (255, 215,  0),   # gold
        "timer":  3.0,       # very short window
        "chance": 10,        # rarest
    },
]

# Pre-build a weighted pool list for random.choice():
# each type appears (chance) times so pick probability matches weights.
FOOD_POOL = []
for ft in FOOD_TYPES:
    FOOD_POOL.extend([ft] * ft["chance"])

# ── Display setup ─────────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT + HUD_HEIGHT))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

# ── Fonts ────────────────────────────────────────────────────────
font_hud   = pygame.font.SysFont("Courier New", 20, bold=True)
font_big   = pygame.font.SysFont("Courier New", 42, bold=True)
font_small = pygame.font.SysFont("Courier New", 22)
font_tiny  = pygame.font.SysFont("Courier New", 13)
font_timer = pygame.font.SysFont("Courier New", 11, bold=True)


# ─────────────────────────────────────────────────────────────────
# Helper – draw one grid cell
# ─────────────────────────────────────────────────────────────────
def draw_cell(surface, col, row, color, margin=1):
    """Fill a single grid cell at (col, row) with the given colour."""
    rect = pygame.Rect(
        col * CELL_SIZE + margin,
        row * CELL_SIZE + margin + HUD_HEIGHT,
        CELL_SIZE - margin * 2,
        CELL_SIZE - margin * 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=3)


# ─────────────────────────────────────────────────────────────────
# Helper – draw border walls
# ─────────────────────────────────────────────────────────────────
def draw_walls(surface):
    """Render the outer wall ring (row 0, row ROWS-1, col 0, col COLS-1)."""
    for col in range(COLS):
        draw_cell(surface, col, 0,        WALL_COLOR, margin=0)   # top
        draw_cell(surface, col, ROWS - 1, WALL_COLOR, margin=0)   # bottom
    for row in range(1, ROWS - 1):
        draw_cell(surface, 0,        row, WALL_COLOR, margin=0)   # left
        draw_cell(surface, COLS - 1, row, WALL_COLOR, margin=0)   # right


# ─────────────────────────────────────────────────────────────────
# Helper – HUD bar
# ─────────────────────────────────────────────────────────────────
def draw_hud(surface, score, level, fps):
    """Render score, level, and speed in the top HUD bar."""
    pygame.draw.rect(surface, (15, 15, 15), (0, 0, WIDTH, HUD_HEIGHT))
    pygame.draw.line(surface, DARK_GREEN, (0, HUD_HEIGHT - 1), (WIDTH, HUD_HEIGHT - 1), 1)

    surface.blit(font_hud.render(f"SCORE: {score}", True, GREEN),  (14, 10))
    lv = font_hud.render(f"LEVEL: {level}", True, YELLOW)
    surface.blit(lv, (WIDTH // 2 - lv.get_width() // 2, 10))
    sp = font_hud.render(f"SPD: {fps}", True, GRAY)
    surface.blit(sp, (WIDTH - sp.get_width() - 14, 10))


# ─────────────────────────────────────────────────────────────────
# Helper – food legend
# ─────────────────────────────────────────────────────────────────
def draw_legend(surface):
    """
    Draw a small legend in the bottom-right corner showing each food
    type with its colour, points, grow bonus, and timer duration.
    """
    x_start = WIDTH - 148
    y_start = HEIGHT + HUD_HEIGHT - len(FOOD_TYPES) * 18 - 6

    for i, ft in enumerate(FOOD_TYPES):
        y = y_start + i * 18
        pygame.draw.circle(surface, ft["color"], (x_start + 6, y + 6), 5)
        timer_str = f"{ft['timer']}s" if ft["timer"] else "inf"
        label = f"{ft['name']}  +{ft['points']}  g:{ft['grow']}  t:{timer_str}"
        surface.blit(font_tiny.render(label, True, GRAY), (x_start + 16, y))


# ─────────────────────────────────────────────────────────────────
# Helper – semi-transparent overlay (title / pause / game-over)
# ─────────────────────────────────────────────────────────────────
def draw_overlay(surface, title, subtitle=""):
    """Darken the screen and display a centred title and subtitle."""
    veil = pygame.Surface((WIDTH, HEIGHT + HUD_HEIGHT), pygame.SRCALPHA)
    veil.fill((0, 0, 0, 160))
    surface.blit(veil, (0, 0))

    ts = font_big.render(title, True, GREEN)
    surface.blit(ts, (WIDTH // 2 - ts.get_width() // 2,
                      (HEIGHT + HUD_HEIGHT) // 2 - 50))
    if subtitle:
        ss = font_small.render(subtitle, True, WHITE)
        surface.blit(ss, (WIDTH // 2 - ss.get_width() // 2,
                          (HEIGHT + HUD_HEIGHT) // 2 + 10))


# ─────────────────────────────────────────────────────────────────
# Food item class
# ─────────────────────────────────────────────────────────────────
class FoodItem:
    """
    Represents one piece of food on the board.

    Attributes
    ----------
    pos        : (col, row) grid position
    food_type  : one dict from FOOD_TYPES
    time_left  : seconds remaining (float) or None for immortal food
    """

    def __init__(self, pos, food_type):
        self.pos       = pos
        self.food_type = food_type
        # Copy the timer value so each instance counts down independently
        self.time_left = food_type["timer"]   # float or None

    # ── Convenience properties ────────────────────────────────────
    @property
    def color(self):
        return self.food_type["color"]

    @property
    def points(self):
        """Score value of this food — the food's 'weight'."""
        return self.food_type["points"]

    @property
    def grow(self):
        """How many tail segments to add when this food is eaten."""
        return self.food_type["grow"]

    # ── Timer update ──────────────────────────────────────────────
    def update(self, dt):
        """
        Subtract dt seconds from the countdown.
        Returns True when the food has expired and must be removed.
        Immortal food (time_left is None) always returns False.
        """
        if self.time_left is None:
            return False           # immortal — never expires
        self.time_left -= dt
        return self.time_left <= 0

    # ── Rendering ─────────────────────────────────────────────────
    def draw(self, surface):
        """
        Draw the food circle on the board.
          - Blinking: timed foods blink when < 2 seconds remain
          - Countdown: a number above the food shows seconds left
          - Highlight: dot size reflects the point value (weight)
        """
        col, row = self.pos
        cx = col * CELL_SIZE + CELL_SIZE // 2
        cy = row * CELL_SIZE + CELL_SIZE // 2 + HUD_HEIGHT

        # ── Blink when about to expire ────────────────────────────
        # Use get_ticks() to build a 250 ms blink cycle.
        # When time_left < 2 s, alternate visible/invisible.
        if self.time_left is not None and self.time_left < 2.0:
            if (pygame.time.get_ticks() // 250) % 2 == 0:
                return    # invisible on this half-cycle → blink effect

        # ── Main filled circle ────────────────────────────────────
        pygame.draw.circle(surface, self.color, (cx, cy), CELL_SIZE // 2 - 2)

        # ── Highlight dot — size shows the food's point weight ────
        # Maps 10 pts → radius 2, 100 pts → radius 5
        highlight_r = max(2, min(5, self.points // 20))
        pygame.draw.circle(surface, WHITE, (cx - 3, cy - 3), highlight_r)

        # ── Countdown timer label (shown above the circle) ────────
        if self.time_left is not None:
            secs = max(0, int(self.time_left) + 1)   # ceil for display
            t_surf = font_timer.render(str(secs), True, WHITE)
            surface.blit(t_surf, (cx - t_surf.get_width() // 2,
                                  cy - CELL_SIZE // 2 - 13))


# ─────────────────────────────────────────────────────────────────
# Helper – spawn one food item at a valid free cell
# ─────────────────────────────────────────────────────────────────
def spawn_food(snake_body, existing_foods):
    """
    Choose a weighted-random food type from FOOD_POOL and place it
    at a grid cell that is:
      - Inside the walls  (col 1..COLS-2,  row 1..ROWS-2)
      - Not on the snake  body
      - Not on an existing food item
    Returns a FoodItem, or None if no free cell was found.
    """
    # Combine all occupied cells into a set for O(1) lookup
    occupied = set(snake_body) | {f.pos for f in existing_foods}

    # All playable cells not currently occupied
    free_cells = [
        (c, r)
        for c in range(1, COLS - 1)
        for r in range(1, ROWS - 1)
        if (c, r) not in occupied
    ]

    if not free_cells:
        return None    # board too crowded

    pos       = random.choice(free_cells)       # random free position
    food_type = random.choice(FOOD_POOL)        # weighted random type
    return FoodItem(pos, food_type)


# ─────────────────────────────────────────────────────────────────
# Main game loop
# ─────────────────────────────────────────────────────────────────
def main():

    # ── Snake initial state ───────────────────────────────────────
    # List of (col, row) tuples; index 0 is the head
    snake       = [(COLS // 2,     ROWS // 2),
                   (COLS // 2 - 1, ROWS // 2),
                   (COLS // 2 - 2, ROWS // 2)]

    direction   = (1, 0)    # moving right at start
    next_dir    = (1, 0)    # buffered direction (applied each tick)

    # ── Score / level ────────────────────────────────────────────
    score       = 0
    level       = 1
    food_eaten  = 0          # resets to 0 each level
    current_fps = BASE_FPS

    # ── Food list ────────────────────────────────────────────────
    # Multiple FoodItem objects can coexist on the board at once
    foods = []
    first = spawn_food(snake, foods)
    if first:
        foods.append(first)

    # Automatic periodic spawn timer (counts up in seconds)
    spawn_timer = 0.0

    # ── Game state machine ────────────────────────────────────────
    state = "START"    # states: START | RUNNING | PAUSED | DEAD

    # ── Main loop ─────────────────────────────────────────────────
    while True:

        # Compute delta-time in seconds; also enforces the FPS cap.
        # dt is used for all timer countdowns so they stay real-time
        # even if the frame rate changes between levels.
        dt = clock.tick(current_fps) / 1000.0

        # ── Event handling ────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                # SPACE / ENTER — start, restart, or resume
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if state in ("START", "DEAD"):
                        # Full game reset
                        snake       = [(COLS // 2,     ROWS // 2),
                                       (COLS // 2 - 1, ROWS // 2),
                                       (COLS // 2 - 2, ROWS // 2)]
                        direction   = (1, 0)
                        next_dir    = (1, 0)
                        score       = 0
                        level       = 1
                        food_eaten  = 0
                        current_fps = BASE_FPS
                        foods       = []
                        spawn_timer = 0.0
                        first = spawn_food(snake, foods)
                        if first:
                            foods.append(first)
                        state = "RUNNING"
                    elif state == "PAUSED":
                        state = "RUNNING"

                # P — pause / unpause
                elif event.key == pygame.K_p:
                    if state == "RUNNING":
                        state = "PAUSED"
                    elif state == "PAUSED":
                        state = "RUNNING"

                # Direction input — arrow keys and WASD.
                # Guard: don't allow a 180° reversal in one frame.
                elif event.key in (pygame.K_UP, pygame.K_w):
                    if direction != (0, 1):
                        next_dir = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if direction != (0, -1):
                        next_dir = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if direction != (1, 0):
                        next_dir = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if direction != (-1, 0):
                        next_dir = (1, 0)

        # ── Game logic (skip when not RUNNING) ────────────────────
        if state == "RUNNING":

            # Commit the buffered direction for this tick
            direction = next_dir

            # Compute where the head will move to
            head     = snake[0]
            new_head = (head[0] + direction[0], head[1] + direction[1])

            # ── Wall collision ────────────────────────────────────
            col, row = new_head
            if col <= 0 or col >= COLS - 1 or row <= 0 or row >= ROWS - 1:
                state = "DEAD"

            # ── Self collision ────────────────────────────────────
            elif new_head in snake:
                state = "DEAD"

            else:
                # Prepend the new head — snake moves forward
                snake.insert(0, new_head)

                # ── Food collision check ──────────────────────────
                # Find the first food whose position matches the new head
                eaten = None
                for f in foods:
                    if f.pos == new_head:
                        eaten = f
                        break

                if eaten:
                    # Award points (scaled by current level)
                    score      += eaten.points * level
                    food_eaten += 1

                    # Grow the snake.
                    # We already kept the tail (didn't pop), so the snake
                    # grew by 1. For grow > 1, append extra tail copies.
                    for _ in range(eaten.grow - 1):
                        snake.append(snake[-1])

                    # Remove the eaten food item from the board
                    foods.remove(eaten)

                    # ── Level-up ──────────────────────────────────
                    if food_eaten >= FOOD_PER_LEVEL:
                        level      += 1
                        food_eaten  = 0
                        # Increase game speed, capped at MAX_FPS
                        current_fps = min(MAX_FPS,
                                         BASE_FPS + (level - 1) * FPS_STEP)

                    # Spawn a replacement food immediately
                    replacement = spawn_food(snake, foods)
                    if replacement:
                        foods.append(replacement)

                else:
                    # No food eaten — pop the tail to keep length constant
                    snake.pop()

                # ── Update food timers ────────────────────────────
                # Iterate over a copy (foods[:]) so we can safely remove
                # expired items from the original list during the loop.
                for f in foods[:]:
                    if f.update(dt):     # True → food timer ran out
                        foods.remove(f)

                # ── Periodic automatic food spawn ─────────────────
                # Every SPAWN_INTERVAL seconds, add a new food item
                # (up to MAX_FOODS total) to keep the board interesting.
                spawn_timer += dt
                if spawn_timer >= SPAWN_INTERVAL:
                    spawn_timer = 0.0
                    if len(foods) < MAX_FOODS:
                        extra = spawn_food(snake, foods)
                        if extra:
                            foods.append(extra)

        # ── Drawing ───────────────────────────────────────────────
        screen.fill(BLACK)

        # Subtle background grid dots (playable area only)
        for c in range(1, COLS - 1):
            for r in range(1, ROWS - 1):
                pygame.draw.rect(
                    screen, (18, 18, 18),
                    (c * CELL_SIZE + CELL_SIZE // 2 - 1,
                     r * CELL_SIZE + CELL_SIZE // 2 - 1 + HUD_HEIGHT,
                     2, 2)
                )

        draw_walls(screen)

        # Draw all active food items
        # (each calls its own draw method with blink + timer label)
        for f in foods:
            f.draw(screen)

        # Draw snake — head is brightest, tail fades gradually
        for idx, (c, r) in enumerate(snake):
            if idx == 0:
                color = BRIGHT_GRN   # head
            else:
                fade  = max(0.0, 1.0 - idx / len(snake) * 0.75)
                color = (int(50 * fade), int(200 * fade), int(50 * fade))
            draw_cell(screen, c, r, color)

        draw_hud(screen, score, level, current_fps)
        draw_legend(screen)

        # ── Overlay screens ───────────────────────────────────────
        if state == "START":
            draw_overlay(screen, "SNAKE",
                         "SPACE to start  |  WASD / Arrows  |  P = pause")
        elif state == "PAUSED":
            draw_overlay(screen, "PAUSED", "Press P or SPACE to resume")
        elif state == "DEAD":
            draw_overlay(screen, "GAME OVER",
                         f"Score: {score}   Level: {level}   |   SPACE to restart")

        pygame.display.flip()
        # Note: clock.tick() was already called at the top to compute dt


# ── Entry point ───────────────────────────────────────────────────
if __name__ == "__main__":
    main()