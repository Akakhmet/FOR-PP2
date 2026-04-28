"""game.py — Snake game: entities, logic, run_game()."""

import pygame
import random
from collections import deque
from config import *

# ── Directions ────────────────────────────────────────────────────
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

KEY_DIR = {
    pygame.K_UP:    UP,    pygame.K_w: UP,
    pygame.K_DOWN:  DOWN,  pygame.K_s: DOWN,
    pygame.K_LEFT:  LEFT,  pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
}


# ── Entity classes ────────────────────────────────────────────────

class Food:
    # (color, points, lifetime_ms or None)
    VARIANTS = [
        (FOOD_NORMAL, 1, None),
        (FOOD_BONUS,  3, 7000),
        (FOOD_HEAVY,  2, None),
    ]

    def __init__(self, pos):
        self.pos   = pos
        v          = random.choice(self.VARIANTS)
        self.color, self.points, life = v
        self._born  = pygame.time.get_ticks()
        self._life  = life

    def expired(self):
        return self._life is not None and pygame.time.get_ticks() - self._born > self._life


class PoisonFood:
    def __init__(self, pos):
        self.pos   = pos
        self.color = POISON_COL


class PowerUp:
    KINDS  = ["speed", "slow", "shield"]
    COLORS = {"speed": PU_SPEED, "slow": PU_SLOW, "shield": PU_SHIELD}

    def __init__(self, pos):
        self.pos   = pos
        self.kind  = random.choice(self.KINDS)
        self.color = self.COLORS[self.kind]
        self._born = pygame.time.get_ticks()

    def expired(self):
        return pygame.time.get_ticks() - self._born > 8000


# ── Helpers ───────────────────────────────────────────────────────

def _all_cells():
    return {(c, r) for c in range(COLS) for r in range(ROWS)}


def _free_cell(occupied):
    free = list(_all_cells() - occupied)
    return random.choice(free) if free else None


def _occupied_set(snake, foods, poison, powerup, obstacles):
    s = set(snake) | obstacles
    for f in foods:
        s.add(f.pos)
    if poison:
        s.add(poison.pos)
    if powerup:
        s.add(powerup.pos)
    return s


def _reachable(head, snake_set, obstacles):
    """BFS count of cells reachable from head (ignoring snake body except head)."""
    visited = {head}
    queue   = deque([head])
    blocked = snake_set | obstacles
    while queue:
        cx, cy = queue.popleft()
        for dx, dy in [UP, DOWN, LEFT, RIGHT]:
            npos = (cx + dx, cy + dy)
            if (npos not in visited
                    and 0 <= npos[0] < COLS
                    and 0 <= npos[1] < ROWS
                    and npos not in blocked):
                visited.add(npos)
                queue.append(npos)
    return len(visited)


def _place_obstacles(snake, current_obs, count):
    """Add `count` new obstacles ensuring snake head stays reachable."""
    snake_set = set(snake)
    occupied  = snake_set | current_obs
    obs       = set(current_obs)
    head      = snake[0]
    placed    = 0
    attempts  = 0

    while placed < count and attempts < 500:
        attempts += 1
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if pos in occupied:
            continue
        obs.add(pos)
        if _reachable(head, snake_set, obs) >= 15:
            occupied.add(pos)
            placed += 1
        else:
            obs.remove(pos)

    return obs


# ── Draw helpers ──────────────────────────────────────────────────

def _cell_rect(col, row):
    return pygame.Rect(col * CELL, HUD_H + row * CELL, CELL, CELL)


def _draw_cell(surface, color, col, row, shrink=2):
    r = _cell_rect(col, row).inflate(-shrink, -shrink)
    pygame.draw.rect(surface, color, r, border_radius=3)


# ── Main game function ────────────────────────────────────────────

def run_game(screen, settings, player_id, personal_best):
    """
    Run one snake game. Returns {"score": int, "level": int} or None on ESC.
    """
    clock = pygame.time.Clock()

    snake_color = tuple(settings.get("snake_color", list(SNAKE_DEFAULT)))
    head_color  = tuple(min(c + 40, 255) for c in snake_color)
    grid_on     = settings.get("grid", True)
    sound_on    = settings.get("sound", True)

    # Eat / die sounds (silent fallback)
    eat_snd = die_snd = None
    if sound_on:
        try:
            eat_snd = pygame.mixer.Sound("assets/eat.wav")
            die_snd = pygame.mixer.Sound("assets/die.wav")
        except Exception:
            pass

    # ── Initial state ─────────────────────────────────────────────
    snake   = [(COLS // 2, ROWS // 2),
               (COLS // 2 - 1, ROWS // 2),
               (COLS // 2 - 2, ROWS // 2)]
    direction  = RIGHT
    next_dir   = RIGHT

    score      = 0
    level      = 1
    foods_eaten= 0
    obstacles  = set()

    foods   = [Food(_free_cell(set(snake)))]
    poison  = None
    powerup = None

    # Active effect: {"kind": "speed"|"slow"|"shield", "end_ms": int}
    effect       = None
    shield_ready = False

    last_step_ms  = pygame.time.get_ticks()
    last_pu_ms    = pygame.time.get_ticks()
    last_psn_ms   = pygame.time.get_ticks()

    font_sm = pygame.font.SysFont("Verdana", 15)
    font_md = pygame.font.SysFont("Verdana", 20)
    font_lg = pygame.font.SysFont("Verdana", 28)

    def current_speed():
        spd = SPEED_BASE + (level - 1) * SPEED_STEP
        if effect:
            if effect["kind"] == "speed":
                spd += SPEED_BOOST
            elif effect["kind"] == "slow":
                spd = max(3, spd + SPEED_SLOW)
        return min(spd, SPEED_MAX)

    def step_interval():
        return 1000 // current_speed()

    running = True
    dead    = False

    while running:
        now = pygame.time.get_ticks()

        # ── Events ───────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                nd = KEY_DIR.get(event.key)
                if nd and nd != OPPOSITE.get(direction):
                    next_dir = nd

        # ── Effect expiry ─────────────────────────────────────────
        if effect and now > effect["end_ms"]:
            if effect["kind"] != "shield":
                effect = None

        # ── Spawn poison periodically ─────────────────────────────
        if poison is None and now - last_psn_ms > 12000:
            last_psn_ms = now
            occ = _occupied_set(snake, foods, None, powerup, obstacles)
            pos = _free_cell(occ)
            if pos:
                poison = PoisonFood(pos)

        # ── Spawn power-up periodically ───────────────────────────
        if powerup is None and now - last_pu_ms > 10000:
            last_pu_ms = now
            occ = _occupied_set(snake, foods, poison, None, obstacles)
            pos = _free_cell(occ)
            if pos:
                powerup = PowerUp(pos)

        # ── Expire food and power-up ──────────────────────────────
        foods   = [f for f in foods if not f.expired()]
        if not foods:
            occ = _occupied_set(snake, [], poison, powerup, obstacles)
            pos = _free_cell(occ)
            if pos:
                foods.append(Food(pos))
        if powerup and powerup.expired():
            powerup = None

        # ── Snake step ────────────────────────────────────────────
        if now - last_step_ms >= step_interval():
            last_step_ms = now
            direction    = next_dir
            dx, dy       = direction
            head         = (snake[0][0] + dx, snake[0][1] + dy)

            # Wall collision
            if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):
                if shield_ready:
                    shield_ready = False
                    effect       = None
                    # Bounce: wrap to opposite side
                    head = (head[0] % COLS, head[1] % ROWS)
                else:
                    dead = True

            # Self-collision
            if not dead and head in set(snake[:-1]):
                if shield_ready:
                    shield_ready = False
                    effect       = None
                else:
                    dead = True

            # Obstacle collision
            if not dead and head in obstacles:
                if shield_ready:
                    shield_ready = False
                    effect       = None
                else:
                    dead = True

            if dead:
                if die_snd:
                    die_snd.play()
                break

            # Move snake
            snake.insert(0, head)
            grew = False

            # Eat normal food
            for f in foods[:]:
                if head == f.pos:
                    score       += f.points
                    foods_eaten += 1
                    foods.remove(f)
                    grew = True
                    if eat_snd:
                        eat_snd.play()
                    occ = _occupied_set(snake, foods, poison, powerup, obstacles)
                    pos = _free_cell(occ)
                    if pos:
                        foods.append(Food(pos))
                    break

            # Eat poison
            if poison and head == poison.pos:
                poison = None
                grew   = False
                # Shorten by 2
                snake  = snake[:-min(2, len(snake) - 1)]
                if len(snake) <= 1:
                    dead = True
                    break

            # Collect power-up
            if powerup and head == powerup.pos:
                kind    = powerup.kind
                powerup = None
                last_pu_ms = now
                if kind == "shield":
                    shield_ready = True
                    effect       = {"kind": "shield", "end_ms": now + 999999}
                else:
                    effect = {"kind": kind, "end_ms": now + 5000}

            if not grew:
                snake.pop()

            # Level up
            if foods_eaten >= level * FOODS_PER_LEVEL:
                level += 1
                if level >= OBS_START_LEVEL:
                    obstacles = _place_obstacles(snake, obstacles, OBS_PER_LEVEL)

        # ── Draw ─────────────────────────────────────────────────
        screen.fill(BG)

        # HUD background
        pygame.draw.rect(screen, (25, 25, 45), (0, 0, SW, HUD_H))
        pygame.draw.line(screen, GRAY, (0, HUD_H - 1), (SW, HUD_H - 1))

        # HUD text
        screen.blit(font_sm.render(f"Score: {score}",         True, WHITE),  (8,  8))
        screen.blit(font_sm.render(f"Level: {level}",         True, WHITE),  (8, 30))
        screen.blit(font_sm.render(f"Best:  {personal_best}", True, (180,180,255)), (8, 50))

        next_lv = level * FOODS_PER_LEVEL
        screen.blit(font_sm.render(f"Food: {foods_eaten}/{next_lv}", True, GRAY), (170, 8))
        screen.blit(font_sm.render(f"Spd: {current_speed()}",        True, GRAY), (170, 30))

        if effect:
            et   = max(0, (effect["end_ms"] - now) // 1000)
            kind = effect["kind"]
            col  = {"speed": PU_SPEED, "slow": PU_SLOW, "shield": PU_SHIELD}[kind]
            label = f"{'SHIELD' if kind=='shield' else kind.upper()+f'  {et}s'}"
            screen.blit(font_sm.render(label, True, col), (340, 8))

        # Grid
        if grid_on:
            for c in range(COLS + 1):
                x = c * CELL
                pygame.draw.line(screen, GRID_COLOR, (x, HUD_H), (x, SH))
            for r in range(ROWS + 1):
                y = HUD_H + r * CELL
                pygame.draw.line(screen, GRID_COLOR, (0, y), (SW, y))

        # Obstacles
        for pos in obstacles:
            _draw_cell(screen, WALL_COLOR, *pos, shrink=1)

        # Food
        for f in foods:
            _draw_cell(screen, f.color, *f.pos)

        # Poison
        if poison:
            _draw_cell(screen, poison.color, *poison.pos)

        # Power-up
        if powerup:
            r = _cell_rect(*powerup.pos).inflate(-3, -3)
            pygame.draw.ellipse(screen, powerup.color, r)
            lbl = pygame.font.SysFont("Verdana", 11, bold=True).render(
                powerup.kind[0].upper(), True, BLACK)
            screen.blit(lbl, lbl.get_rect(center=r.center))

        # Snake body
        for i, seg in enumerate(snake):
            color = head_color if i == 0 else snake_color
            _draw_cell(screen, color, *seg, shrink=2 if i > 0 else 1)

        pygame.display.flip()
        clock.tick(60)

    return {"score": score, "level": level}
