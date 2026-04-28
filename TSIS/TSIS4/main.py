
import pygame
import json
import os
import sys
from pygame.locals import *

import db
from game import run_game
from config import *

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "snake_color": list(SNAKE_DEFAULT),
    "grid":        True,
    "sound":       True,
}

COLOR_OPTIONS = [
    ("Green",  [40, 180, 40]),
    ("Blue",   [30, 80,  220]),
    ("Red",    [210, 40, 40]),
    ("Purple", [150, 40, 200]),
    ("Teal",   [20, 180, 170]),
]

# ── Settings I/O ─────────────────────────────────────────────────

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return {**DEFAULT_SETTINGS, **json.load(f)}
    return DEFAULT_SETTINGS.copy()


def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)


# ── UI helpers ────────────────────────────────────────────────────

_fonts = {}
def _f(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("Verdana", size, bold=bold)
    return _fonts[key]


def _bg(screen):
    screen.fill(BG)


class Button:
    def __init__(self, text, rect, color=(40,40,65), hcolor=(70,70,110), tcolor=WHITE):
        self.text   = text
        self.rect   = pygame.Rect(rect)
        self.color  = color
        self.hcolor = hcolor
        self.tcolor = tcolor

    def draw(self, screen):
        c = self.hcolor if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(screen, c, self.rect, border_radius=8)
        pygame.draw.rect(screen, GRAY, self.rect, 2, border_radius=8)
        lbl = _f(16).render(self.text, True, self.tcolor)
        screen.blit(lbl, lbl.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (event.type == MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


# ── Screens ───────────────────────────────────────────────────────

def username_screen(screen):
    """Returns typed username string or None on ESC."""
    clock = pygame.time.Clock()
    name  = ""
    box   = pygame.Rect(SW // 2 - 130, 260, 260, 46)

    while True:
        _bg(screen)
        screen.blit(_f(38, True).render("🐍 SNAKE", True, (40, 210, 80)),
                    _f(38, True).render("🐍 SNAKE", True, (40, 210, 80)).get_rect(center=(SW//2, 130)))
        screen.blit(_f(20).render("Enter your username", True, WHITE),
                    _f(20).render("Enter your username", True, WHITE).get_rect(center=(SW//2, 210)))

        pygame.draw.rect(screen, WHITE, box, border_radius=6)
        screen.blit(_f(22).render(name + "|", True, BLACK), (box.x + 8, box.y + 10))

        screen.blit(_f(14).render("Enter = confirm   Esc = quit", True, GRAY),
                    _f(14).render("Enter = confirm   Esc = quit", True, GRAY).get_rect(center=(SW//2, 340)))

        for event in pygame.event.get():
            if event.type == QUIT:
                return None
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    return name.strip()
                elif event.key == K_ESCAPE:
                    return None
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 18 and event.unicode.isprintable():
                    name += event.unicode

        pygame.display.flip()
        clock.tick(60)


def main_menu(screen, username):
    """Returns next state string."""
    clock = pygame.time.Clock()
    cx    = SW // 2
    btns  = {
        "game":        Button("Play",        (cx-80, 200, 160, 44)),
        "leaderboard": Button("Leaderboard", (cx-80, 258, 160, 44)),
        "settings":    Button("Settings",    (cx-80, 316, 160, 44)),
        "quit":        Button("Quit",        (cx-80, 374, 160, 44), (120,20,20), (180,40,40)),
    }
    while True:
        _bg(screen)
        screen.blit(_f(42, True).render("SNAKE", True, (40, 210, 80)),
                    _f(42, True).render("SNAKE", True, (40, 210, 80)).get_rect(center=(cx, 90)))
        screen.blit(_f(16).render(f"Player:  {username}", True, GRAY),
                    _f(16).render(f"Player:  {username}", True, GRAY).get_rect(center=(cx, 145)))

        for btn in btns.values():
            btn.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            for key, btn in btns.items():
                if btn.clicked(event):
                    return key

        pygame.display.flip()
        clock.tick(60)


def game_over_screen(screen, result, personal_best):
    """Returns next state string."""
    clock = pygame.time.Clock()
    cx    = SW // 2
    btns  = {
        "game":  Button("Retry",     (cx - 130, 420, 120, 42)),
        "menu":  Button("Main Menu", (cx + 10,  420, 120, 42)),
    }
    new_best = result["score"] > personal_best

    while True:
        _bg(screen)
        screen.blit(_f(36, True).render("Game Over", True, (220, 50, 50)),
                    _f(36, True).render("Game Over", True, (220, 50, 50)).get_rect(center=(cx, 110)))

        for i, (label, val) in enumerate([
            ("Score",         result["score"]),
            ("Level reached", result["level"]),
            ("Personal best", result["score"] if new_best else personal_best),
        ]):
            line = _f(20).render(f"{label}:   {val}", True, WHITE)
            screen.blit(line, line.get_rect(center=(cx, 220 + i * 50)))

        if new_best:
            nb = _f(18, True).render("🏆 New personal best!", True, (212, 175, 55))
            screen.blit(nb, nb.get_rect(center=(cx, 360)))

        for btn in btns.values():
            btn.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            for key, btn in btns.items():
                if btn.clicked(event):
                    return key

        pygame.display.flip()
        clock.tick(60)


def leaderboard_screen(screen):
    """Fetches DB and displays top-10."""
    clock = pygame.time.Clock()
    back  = Button("Back", (SW // 2 - 60, SH - 55, 120, 38))

    try:
        rows = db.get_leaderboard()
    except Exception as e:
        rows = []
        print(f"[DB] {e}")

    while True:
        _bg(screen)
        screen.blit(_f(26, True).render("Leaderboard", True, (212, 175, 55)),
                    _f(26, True).render("Leaderboard", True, (212, 175, 55)).get_rect(center=(SW//2, 35)))

        hdr = _f(13).render("Rank  Username         Score   Lvl   Date", True, GRAY)
        screen.blit(hdr, (14, 68))
        pygame.draw.line(screen, GRAY, (14, 86), (SW - 14, 86))

        for i, row in enumerate(rows):
            name, score, level, dt = row
            color = (212, 175, 55) if i == 0 else WHITE
            line  = f"#{i+1:<4} {name:<16} {score:<8} {level:<6} {dt}"
            screen.blit(_f(14).render(line, True, color), (14, 92 + i * 38))

        if not rows:
            screen.blit(_f(18).render("No scores yet!", True, GRAY),
                        _f(18).render("No scores yet!", True, GRAY).get_rect(center=(SW//2, 300)))

        back.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if back.clicked(event) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return

        pygame.display.flip()
        clock.tick(60)


def settings_screen(screen, settings):
    """Returns (possibly modified) settings dict."""
    clock = pygame.time.Clock()
    s     = settings.copy()
    cx    = SW // 2

    color_names = [name for name, _ in COLOR_OPTIONS]
    color_vals  = [val  for _, val  in COLOR_OPTIONS]

    def _cur_color_idx():
        for i, v in enumerate(color_vals):
            if list(s["snake_color"]) == v:
                return i
        return 0

    color_idx = _cur_color_idx()

    grid_btn  = Button("", (cx + 30, 170, 120, 36))
    sound_btn = Button("", (cx + 30, 225, 120, 36))
    color_btn = Button("", (cx + 30, 280, 120, 36))
    back_btn  = Button("Save & Back", (cx - 80, 460, 160, 42), (30, 120, 30), (50, 170, 50))

    while True:
        _bg(screen)
        screen.blit(_f(28, True).render("Settings", True, WHITE),
                    _f(28, True).render("Settings", True, WHITE).get_rect(center=(cx, 90)))

        for label, y in [("Grid overlay:", 178), ("Sound:", 233), ("Snake color:", 288)]:
            screen.blit(_f(16).render(label, True, GRAY), (40, y))

        grid_btn.text  = "ON"  if s["grid"]  else "OFF"
        sound_btn.text = "ON"  if s["sound"] else "OFF"
        color_btn.text = color_names[color_idx]
        color_btn.color = tuple(color_vals[color_idx])

        for btn in [grid_btn, sound_btn, color_btn, back_btn]:
            btn.draw(screen)

        # Color preview swatch
        pygame.draw.rect(screen, tuple(color_vals[color_idx]),
                         pygame.Rect(cx + 155, 282, 22, 22), border_radius=4)

        for event in pygame.event.get():
            if event.type == QUIT:
                return s
            if grid_btn.clicked(event):
                s["grid"] = not s["grid"]
            if sound_btn.clicked(event):
                s["sound"] = not s["sound"]
            if color_btn.clicked(event):
                color_idx = (color_idx + 1) % len(color_names)
                s["snake_color"] = color_vals[color_idx]
            if back_btn.clicked(event) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return s

        pygame.display.flip()
        clock.tick(60)


# ── Entry point ───────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption("Snake — TSIS 4")

    # Init DB
    try:
        db.init_db()
    except Exception as e:
        print(f"[DB] Could not connect: {e}")

    settings = load_settings()

    # Username entry (once per launch)
    username  = username_screen(screen)
    if not username:
        pygame.quit()
        sys.exit()

    player_id     = None
    personal_best = 0
    try:
        player_id     = db.get_or_create_player(username)
        personal_best = db.get_personal_best(player_id)
    except Exception as e:
        print(f"[DB] {e}")

    state  = "menu"
    result = None

    while True:
        if state == "menu":
            state = main_menu(screen, username)

        elif state == "game":
            result = run_game(screen, settings, player_id, personal_best)
            if result is None:
                state = "menu"
            else:
                try:
                    if player_id:
                        db.save_session(player_id, result["score"], result["level"])
                        personal_best = db.get_personal_best(player_id)
                except Exception as e:
                    print(f"[DB] {e}")
                state = "gameover"

        elif state == "gameover":
            state = game_over_screen(screen, result, personal_best)

        elif state == "leaderboard":
            leaderboard_screen(screen)
            state = "menu"

        elif state == "settings":
            settings = settings_screen(screen, settings)
            save_settings(settings)
            state = "menu"

        elif state == "quit":
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
