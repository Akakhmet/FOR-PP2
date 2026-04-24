"""
Snake entity: movement, collision, growth.
"""
from settings import (
    COLS, ROWS, BRIGHT_GRN, GREEN, CELL_SIZE, HUD_HEIGHT
)


class Snake:
    """Represents the snake with position, direction, and rendering."""

    def __init__(self, start_pos=None):
        """Initialize snake with 3 segments at center or given position."""
        if start_pos is None:
            start_pos = (COLS // 2, ROWS // 2)
        self.body = [
            start_pos,
            (start_pos[0] - 1, start_pos[1]),
            (start_pos[0] - 2, start_pos[1]),
        ]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

    @property
    def head(self):
        """Return head position (first element of body)."""
        return self.body[0]

    def set_direction(self, new_dir):
        """Buffer direction change, preventing 180° reversal."""
        if (new_dir[0] + self.direction[0], new_dir[1] + self.direction[1]) != (0, 0):
            self.next_direction = new_dir

    def apply_direction(self):
        """Commit buffered direction to active direction."""
        self.direction = self.next_direction

    def move(self, grow=False):
        """
        Advance snake by one step.
        If grow=False, remove tail to maintain length.
        Returns new head position.
        """
        head = self.head
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()
        return new_head

    def check_wall_collision(self, position=None):
        """Return True if position hits outer wall border."""
        col, row = position if position else self.head
        return col <= 0 or col >= COLS - 1 or row <= 0 or row >= ROWS - 1

    def check_self_collision(self, position=None):
        """Return True if position collides with snake body (excluding head)."""
        pos = position if position else self.head
        return pos in self.body[1:]

    def get_color_for_segment(self, index):
        """Return color for segment: brightest at head, fading toward tail."""
        if index == 0:
            return BRIGHT_GRN
        fade = max(0, 1.0 - index / len(self.body) * 0.75)
        return (int(50 * fade), int(200 * fade), int(50 * fade))

    def draw(self, surface):
        """Render all snake segments with gradient coloring."""
        from utils import draw_cell
        for idx, (c, r) in enumerate(self.body):
            color = self.get_color_for_segment(idx)
            draw_cell(surface, c, r, color)

    def reset(self):
        """Reset snake to initial state at center."""
        start_pos = (COLS // 2, ROWS // 2)
        self.body = [
            start_pos,
            (start_pos[0] - 1, start_pos[1]),
            (start_pos[0] - 2, start_pos[1]),
        ]
        self.direction = (1, 0)
        self.next_direction = (1, 0)