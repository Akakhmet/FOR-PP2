"""tools.py — drawing helpers for paint.py"""

import pygame
from collections import deque


def draw_line_smooth(surface, color, start, end, width):
    """Draw a thick line by interpolating circles (used by pencil & line)."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    steps = max(abs(dx), abs(dy), 1)
    for i in range(steps + 1):
        x = int(start[0] + dx * i / steps)
        y = int(start[1] + dy * i / steps)
        pygame.draw.circle(surface, color, (x, y), width // 2)


def flood_fill(surface, start_pos, fill_color):
    """BFS flood-fill on a pygame Surface."""
    x, y = start_pos
    w, h = surface.get_size()

    # Clamp to canvas
    if not (0 <= x < w and 0 <= y < h):
        return

    target_color = surface.get_at((x, y))[:3]
    fill_rgb = fill_color[:3] if len(fill_color) == 4 else fill_color

    if target_color == fill_rgb:
        return

    visited = set()
    queue = deque()
    queue.append((x, y))
    visited.add((x, y))

    while queue:
        cx, cy = queue.popleft()
        surface.set_at((cx, cy), fill_color)

        for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
            if (0 <= nx < w and 0 <= ny < h
                    and (nx, ny) not in visited
                    and surface.get_at((nx, ny))[:3] == target_color):
                visited.add((nx, ny))
                queue.append((nx, ny))