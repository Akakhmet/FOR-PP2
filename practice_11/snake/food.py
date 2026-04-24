"""
Food system: types, spawning, timers, rendering.
"""
import random
import pygame
from settings import (
    CELL_SIZE, COLS, ROWS, HUD_HEIGHT,
    FOOD_POOL, MAX_FOODS, SPAWN_INTERVAL,
    FONT_TIMER, FONT_TINY, WHITE, GRAY, WIDTH, HEIGHT, FOOD_TYPES
)


class FoodItem:
    """
    Represents one piece of food on the board.

    Attributes
    ----------
    pos        : (col, row) grid position
    food_type  : dict from FOOD_TYPES
    time_left  : seconds remaining (float) or None for immortal food
    """

    def __init__(self, pos, food_type):
        self.pos = pos
        self.food_type = food_type
        self.time_left = food_type["timer"]  # float or None

    @property
    def color(self):
        return self.food_type["color"]

    @property
    def points(self):
        """Score value (weight) of this food."""
        return self.food_type["points"]

    @property
    def grow(self):
        """How many tail segments to add when eaten."""
        return self.food_type["grow"]

    @property
    def name(self):
        return self.food_type["name"]

    def update(self, dt):
        """
        Subtract dt seconds from countdown.
        Returns True when food has expired and should be removed.
        """
        if self.time_left is None:
            return False
        self.time_left -= dt
        return self.time_left <= 0

    def draw(self, surface):
        """
        Draw food with:
          - Blinking when < 2 seconds remain
          - Countdown label above
          - Highlight dot size reflects point value
        """
        from utils import get_font

        col, row = self.pos
        cx = col * CELL_SIZE + CELL_SIZE // 2
        cy = row * CELL_SIZE + CELL_SIZE // 2 + HUD_HEIGHT

        # Blink effect when about to expire
        if self.time_left is not None and self.time_left < 2.0:
            if (pygame.time.get_ticks() // 250) % 2 == 0:
                return  # invisible this frame

        # Main circle
        pygame.draw.circle(surface, self.color, (cx, cy), CELL_SIZE // 2 - 2)

        # Highlight dot — size reflects point weight
        highlight_r = max(2, min(5, self.points // 20))
        pygame.draw.circle(surface, WHITE, (cx - 3, cy - 3), highlight_r)

        # Countdown label
        if self.time_left is not None:
            secs = max(0, int(self.time_left) + 1)
            font = get_font(*FONT_TIMER)
            t_surf = font.render(str(secs), True, WHITE)
            surface.blit(t_surf, (cx - t_surf.get_width() // 2,
                                  cy - CELL_SIZE // 2 - 13))


def spawn_food(snake_body, existing_foods):
    """
    Spawn one FoodItem at a valid free cell with weighted-random type.
    Returns FoodItem or None if no free cell available.
    """
    occupied = set(snake_body) | {f.pos for f in existing_foods}
    free_cells = [
        (c, r)
        for c in range(1, COLS - 1)
        for r in range(1, ROWS - 1)
        if (c, r) not in occupied
    ]
    if not free_cells:
        return None

    pos = random.choice(free_cells)
    food_type = random.choice(FOOD_POOL)
    return FoodItem(pos, food_type)


def draw_legend(surface):
    """Draw food type legend in bottom-right corner."""
    from utils import get_font

    x_start = WIDTH - 148
    y_start = HEIGHT + HUD_HEIGHT - len(FOOD_TYPES) * 18 - 6
    font = get_font(*FONT_TINY)

    for i, ft in enumerate(FOOD_TYPES):
        y = y_start + i * 18
        pygame.draw.circle(surface, ft["color"], (x_start + 6, y + 6), 5)
        timer_str = f"{ft['timer']}s" if ft["timer"] else "inf"
        label = f"{ft['name']}  +{ft['points']}  g:{ft['grow']}  t:{timer_str}"
        surface.blit(font.render(label, True, GRAY), (x_start + 16, y))