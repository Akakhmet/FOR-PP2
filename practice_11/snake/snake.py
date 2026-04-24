"""
Snake entity: movement, collision, growth, rendering.
"""
from settings import COLS, ROWS, BRIGHT_GRN, GREEN


class Snake:
    """Represents the snake with position, direction, and rendering."""

    def __init__(self, start_pos=None):
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
        return self.body[0]

    def set_direction(self, new_dir):
        """Buffer direction change, preventing 180° reversal."""
        if (new_dir[0] + self.direction[0], new_dir[1] + self.direction[1]) != (0, 0):
            self.next_direction = new_dir

    def apply_direction(self):
        """Commit buffered direction."""
        self.direction = self.next_direction

    def move_step(self, new_head, grow=False):
        """
        Advance snake to new_head.
        If grow=False, pop tail to maintain length.
        """
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def grow_by(self, count):
        """Append extra tail segments (used when eating food with grow > 1)."""
        for _ in range(count):
            self.body.append(self.body[-1])

    def check_wall_collision(self, position):
        """Return True if position hits outer wall border."""
        col, row = position
        return col <= 0 or col >= COLS - 1 or row <= 0 or row >= ROWS - 1

    def check_self_collision(self, position):
        """Return True if position collides with body (excluding head)."""
        return position in self.body[1:]

    def get_color_for_segment(self, index):
        """Return color: brightest at head, fading toward tail."""
        if index == 0:
            return BRIGHT_GRN
        fade = max(0, 1.0 - index / len(self.body) * 0.75)
        return (int(50 * fade), int(200 * fade), int(50 * fade))

    def draw(self, surface):
        """Render all segments with gradient coloring."""
        from utils import draw_cell
        for idx, (c, r) in enumerate(self.body):
            color = self.get_color_for_segment(idx)
            draw_cell(surface, c, r, color)

    def reset(self):
        """Reset to initial state at center."""
        start_pos = (COLS // 2, ROWS // 2)
        self.body = [
            start_pos,
            (start_pos[0] - 1, start_pos[1]),
            (start_pos[0] - 2, start_pos[1]),
        ]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

    def get_positions_set(self):
        """Return set of all body positions for fast collision lookup."""
        return set(self.body)