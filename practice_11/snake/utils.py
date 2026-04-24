"""
Utility functions for rendering and UI.
"""
import pygame
from settings import (
    CELL_SIZE, COLS, ROWS, WIDTH, HEIGHT, HUD_HEIGHT,
    GREEN, YELLOW, GRAY, WHITE, WALL_COLOR, HUD_BG, GRID_DOT, DARK_GREEN,
    FONT_HUD, FONT_BIG, FONT_SMALL
)

# ── Font cache ──────────────────────────────────────────────────
_fonts = {}

def get_font(name, size, bold=False):
    """Return cached font object."""
    key = (name, size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont(name, size, bold=bold)
    return _fonts[key]


def draw_cell(surface, col, row, color, margin=1, hud_offset=True):
    """Draw a filled rectangle for one grid cell."""
    y_offset = HUD_HEIGHT if hud_offset else 0
    rect = pygame.Rect(
        col * CELL_SIZE + margin,
        row * CELL_SIZE + margin + y_offset,
        CELL_SIZE - margin * 2,
        CELL_SIZE - margin * 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=3)


def draw_walls(surface):
    """Draw outer wall ring around playable area."""
    for col in range(COLS):
        draw_cell(surface, col, 0,         WALL_COLOR, margin=0)
        draw_cell(surface, col, ROWS - 1,  WALL_COLOR, margin=0)
    for row in range(1, ROWS - 1):
        draw_cell(surface, 0,        row,  WALL_COLOR, margin=0)
        draw_cell(surface, COLS - 1, row,  WALL_COLOR, margin=0)


def draw_hud(surface, score, level, fps):
    """Render score, level, and speed in top HUD bar."""
    pygame.draw.rect(surface, HUD_BG, (0, 0, WIDTH, HUD_HEIGHT))
    pygame.draw.line(surface, DARK_GREEN, (0, HUD_HEIGHT - 1), (WIDTH, HUD_HEIGHT - 1), 1)

    font = get_font(*FONT_HUD)
    surface.blit(font.render(f"SCORE: {score}", True, GREEN), (14, 10))
    lv = font.render(f"LEVEL: {level}", True, YELLOW)
    surface.blit(lv, (WIDTH // 2 - lv.get_width() // 2, 10))
    sp = font.render(f"SPD: {fps}", True, GRAY)
    surface.blit(sp, (WIDTH - sp.get_width() - 14, 10))


def draw_overlay(surface, title, subtitle=""):
    """Draw semi-transparent overlay with title and subtitle."""
    overlay = pygame.Surface((WIDTH, HEIGHT + HUD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    title_font = get_font(*FONT_BIG)
    sub_font   = get_font(*FONT_SMALL)

    title_surf = title_font.render(title, True, GREEN)
    surface.blit(title_surf, (
        WIDTH // 2 - title_surf.get_width() // 2,
        (HEIGHT + HUD_HEIGHT) // 2 - 50,
    ))

    if subtitle:
        sub_surf = sub_font.render(subtitle, True, WHITE)
        surface.blit(sub_surf, (
            WIDTH // 2 - sub_surf.get_width() // 2,
            (HEIGHT + HUD_HEIGHT) // 2 + 10,
        ))


def draw_background_grid(surface):
    """Draw subtle background dots in playable area."""
    for c in range(1, COLS - 1):
        for r in range(1, ROWS - 1):
            pygame.draw.rect(
                surface, GRID_DOT,
                (c * CELL_SIZE + CELL_SIZE // 2 - 1,
                 r * CELL_SIZE + CELL_SIZE // 2 - 1 + HUD_HEIGHT,
                 2, 2)
            )