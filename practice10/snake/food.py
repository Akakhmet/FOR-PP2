"""
Food generation and management.
"""
import random
from settings import COLS, ROWS


def random_food(snake_body):
    """
    Choose a random grid cell for food that:
      - Is NOT on the wall border (row/col 0 or max)
      - Is NOT occupied by any snake segment
    Retries until a valid cell is found.
    """
    snake_set = set(snake_body)
    while True:
        col = random.randint(1, COLS - 2)
        row = random.randint(1, ROWS - 2)
        if (col, row) not in snake_set:
            return (col, row)


def draw_food(surface, food_pos):
    """Draw food as a bright red circle with highlight."""
    import pygame
    from settings import RED, CELL_SIZE, HUD_HEIGHT

    cx = food_pos[0] * CELL_SIZE + CELL_SIZE // 2
    cy = food_pos[1] * CELL_SIZE + CELL_SIZE // 2 + HUD_HEIGHT

    pygame.draw.circle(surface, RED, (cx, cy), CELL_SIZE // 2 - 2)
    pygame.draw.circle(surface, (255, 150, 150), (cx - 3, cy - 3), 3)