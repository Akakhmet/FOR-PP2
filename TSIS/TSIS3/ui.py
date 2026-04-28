"""ui.py — All non-gameplay screens: menu, leaderboard, settings, game-over."""

import pygame
from pygame.locals import *

# Palette
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (140, 140, 140)
DARK   = (40,  40,  60)
RED    = (200, 40,  40)
GREEN  = (40,  180, 40)
GOLD   = (212, 175, 55)
BG     = (25,  25,  45)
PANEL  = (35,  35,  60)

_fonts = {}

def _f(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.SysFont("Verdana", size)
    return _fonts[size]

def _bg(screen):
    screen.fill(BG)


# ── Button ────────────────────────────────────────────────────────

class Button:
    def __init__(self, text, rect, color=DARK, hcolor=GRAY, tcolor=WHITE):
        self.text   = text
        self.rect   = pygame.Rect(rect)
        self.color  = color
        self.hcolor = hcolor
        self.tcolor = tcolor

    def draw(self, screen):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, self.hcolor if hover else self.color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        lbl = _f(17).render(self.text, True, self.tcolor)
        screen.blit(lbl, lbl.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (event.type == MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


# ── Screens ───────────────────────────────────────────────────────

def main_menu(screen):
    """Returns next state string."""
    clock = pygame.time.Clock()
    btns = {
        "username":    Button("Play",        (130, 230, 140, 44)),
        "leaderboard": Button("Leaderboard", (130, 288, 140, 44)),
        "settings":    Button("Settings",    (130, 346, 140, 44)),
        "quit":        Button("Quit",        (130, 404, 140, 44), RED, (230, 80, 80)),
    }
    while True:
        _bg(screen)
        title = _f(52).render("RACER", True, GOLD)
        screen.blit(title, title.get_rect(center=(200, 120)))
        sub = _f(17).render("TSIS 3 — Extended Edition", True, GRAY)
        screen.blit(sub, sub.get_rect(center=(200, 180)))

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


def username_screen(screen):
    """Returns name string or None on cancel."""
    clock = pygame.time.Clock()
    name  = ""
    box   = pygame.Rect(80, 270, 240, 44)

    while True:
        _bg(screen)
        screen.blit(_f(26).render("Enter Your Name", True, WHITE),
                    _f(26).render("Enter Your Name", True, WHITE).get_rect(center=(200, 190)))
        pygame.draw.rect(screen, WHITE, box, border_radius=6)
        screen.blit(_f(24).render(name + "|", True, BLACK), (box.x + 8, box.y + 9))
        screen.blit(_f(15).render("Enter = start   Esc = back", True, GRAY),
                    _f(15).render("Enter = start   Esc = back", True, GRAY).get_rect(center=(200, 350)))

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
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        pygame.display.flip()
        clock.tick(60)


def game_over_screen(screen, result):
    """Returns next state string."""
    clock = pygame.time.Clock()
    btns  = {
        "username": Button("Retry",     (70,  440, 120, 42)),
        "menu":     Button("Main Menu", (210, 440, 120, 42)),
    }
    while True:
        _bg(screen)
        screen.blit(_f(48).render("Game Over", True, RED),
                    _f(48).render("Game Over", True, RED).get_rect(center=(200, 100)))

        if result:
            for i, (label, val) in enumerate([
                ("Score",    result["score"]),
                ("Distance", f"{result['distance']} m"),
                ("Coins",    result["coins"]),
            ]):
                line = _f(20).render(f"{label}:  {val}", True, WHITE)
                screen.blit(line, line.get_rect(center=(200, 230 + i * 44)))

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


def leaderboard_screen(screen, lb):
    """Displays top-10; returns when Back is pressed."""
    clock = pygame.time.Clock()
    back  = Button("Back", (150, 535, 100, 40))

    while True:
        _bg(screen)
        screen.blit(_f(26).render("Top 10 Leaderboard", True, GOLD),
                    _f(26).render("Top 10 Leaderboard", True, GOLD).get_rect(center=(200, 35)))

        hdr = _f(14).render("Rank  Name            Score     Dist", True, GRAY)
        screen.blit(hdr, (18, 72))
        pygame.draw.line(screen, GRAY, (18, 90), (382, 90), 1)

        for i, e in enumerate(lb):
            color = GOLD if i == 0 else WHITE
            row = f"#{i+1:<4} {e['name']:<15} {e['score']:<9} {e['distance']}m"
            screen.blit(_f(15).render(row, True, color), (18, 96 + i * 38))

        if not lb:
            screen.blit(_f(18).render("No scores yet!", True, GRAY),
                        _f(18).render("No scores yet!", True, GRAY).get_rect(center=(200, 300)))

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
    clock  = pygame.time.Clock()
    s      = settings.copy()
    colors = ["default", "red", "blue", "green"]
    diffs  = ["easy", "normal", "hard"]

    sound_btn = Button("", (230, 160, 120, 38))
    color_btn = Button("", (230, 218, 120, 38))
    diff_btn  = Button("", (230, 276, 120, 38))
    back_btn  = Button("Save & Back", (130, 490, 140, 42), GREEN, (60, 210, 60))

    while True:
        _bg(screen)
        screen.blit(_f(30).render("Settings", True, WHITE),
                    _f(30).render("Settings", True, WHITE).get_rect(center=(200, 80)))

        for label, y in [("Sound:", 168), ("Car Color:", 226), ("Difficulty:", 284)]:
            screen.blit(_f(17).render(label, True, GRAY), (40, y))

        sound_btn.text = "ON" if s["sound"] else "OFF"
        color_btn.text = s["car_color"].capitalize()
        diff_btn.text  = s["difficulty"].capitalize()

        for btn in [sound_btn, color_btn, diff_btn, back_btn]:
            btn.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                return s
            if sound_btn.clicked(event):
                s["sound"] = not s["sound"]
            if color_btn.clicked(event):
                s["car_color"] = colors[(colors.index(s["car_color"]) + 1) % len(colors)]
            if diff_btn.clicked(event):
                s["difficulty"] = diffs[(diffs.index(s["difficulty"]) + 1) % len(diffs)]
            if back_btn.clicked(event) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return s

        pygame.display.flip()
        clock.tick(60)
"""ui.py — All non-gameplay screens: menu, leaderboard, settings, game-over."""

import pygame
from pygame.locals import *

# Palette
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (140, 140, 140)
DARK   = (40,  40,  60)
RED    = (200, 40,  40)
GREEN  = (40,  180, 40)
GOLD   = (212, 175, 55)
BG     = (25,  25,  45)
PANEL  = (35,  35,  60)

_fonts = {}

def _f(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.SysFont("Verdana", size)
    return _fonts[size]

def _bg(screen):
    screen.fill(BG)


# ── Button ────────────────────────────────────────────────────────

class Button:
    def __init__(self, text, rect, color=DARK, hcolor=GRAY, tcolor=WHITE):
        self.text   = text
        self.rect   = pygame.Rect(rect)
        self.color  = color
        self.hcolor = hcolor
        self.tcolor = tcolor

    def draw(self, screen):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, self.hcolor if hover else self.color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        lbl = _f(17).render(self.text, True, self.tcolor)
        screen.blit(lbl, lbl.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (event.type == MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


# ── Screens ───────────────────────────────────────────────────────

def main_menu(screen):
    """Returns next state string."""
    clock = pygame.time.Clock()
    btns = {
        "username":    Button("Play",        (130, 230, 140, 44)),
        "leaderboard": Button("Leaderboard", (130, 288, 140, 44)),
        "settings":    Button("Settings",    (130, 346, 140, 44)),
        "quit":        Button("Quit",        (130, 404, 140, 44), RED, (230, 80, 80)),
    }
    while True:
        _bg(screen)
        title = _f(52).render("RACER", True, GOLD)
        screen.blit(title, title.get_rect(center=(200, 120)))
        sub = _f(17).render("TSIS 3 — Extended Edition", True, GRAY)
        screen.blit(sub, sub.get_rect(center=(200, 180)))

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


def username_screen(screen):
    """Returns name string or None on cancel."""
    clock = pygame.time.Clock()
    name  = ""
    box   = pygame.Rect(80, 270, 240, 44)

    while True:
        _bg(screen)
        screen.blit(_f(26).render("Enter Your Name", True, WHITE),
                    _f(26).render("Enter Your Name", True, WHITE).get_rect(center=(200, 190)))
        pygame.draw.rect(screen, WHITE, box, border_radius=6)
        screen.blit(_f(24).render(name + "|", True, BLACK), (box.x + 8, box.y + 9))
        screen.blit(_f(15).render("Enter = start   Esc = back", True, GRAY),
                    _f(15).render("Enter = start   Esc = back", True, GRAY).get_rect(center=(200, 350)))

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
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        pygame.display.flip()
        clock.tick(60)


def game_over_screen(screen, result):
    """Returns next state string."""
    clock = pygame.time.Clock()
    btns  = {
        "username": Button("Retry",     (70,  440, 120, 42)),
        "menu":     Button("Main Menu", (210, 440, 120, 42)),
    }
    while True:
        _bg(screen)
        screen.blit(_f(48).render("Game Over", True, RED),
                    _f(48).render("Game Over", True, RED).get_rect(center=(200, 100)))

        if result:
            for i, (label, val) in enumerate([
                ("Score",    result["score"]),
                ("Distance", f"{result['distance']} m"),
                ("Coins",    result["coins"]),
            ]):
                line = _f(20).render(f"{label}:  {val}", True, WHITE)
                screen.blit(line, line.get_rect(center=(200, 230 + i * 44)))

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


def leaderboard_screen(screen, lb):
    """Displays top-10; returns when Back is pressed."""
    clock = pygame.time.Clock()
    back  = Button("Back", (150, 535, 100, 40))

    while True:
        _bg(screen)
        screen.blit(_f(26).render("Top 10 Leaderboard", True, GOLD),
                    _f(26).render("Top 10 Leaderboard", True, GOLD).get_rect(center=(200, 35)))

        hdr = _f(14).render("Rank  Name            Score     Dist", True, GRAY)
        screen.blit(hdr, (18, 72))
        pygame.draw.line(screen, GRAY, (18, 90), (382, 90), 1)

        for i, e in enumerate(lb):
            color = GOLD if i == 0 else WHITE
            row = f"#{i+1:<4} {e['name']:<15} {e['score']:<9} {e['distance']}m"
            screen.blit(_f(15).render(row, True, color), (18, 96 + i * 38))

        if not lb:
            screen.blit(_f(18).render("No scores yet!", True, GRAY),
                        _f(18).render("No scores yet!", True, GRAY).get_rect(center=(200, 300)))

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
    clock  = pygame.time.Clock()
    s      = settings.copy()
    colors = ["default", "red", "blue", "green"]
    diffs  = ["easy", "normal", "hard"]

    sound_btn = Button("", (230, 160, 120, 38))
    color_btn = Button("", (230, 218, 120, 38))
    diff_btn  = Button("", (230, 276, 120, 38))
    back_btn  = Button("Save & Back", (130, 490, 140, 42), GREEN, (60, 210, 60))

    while True:
        _bg(screen)
        screen.blit(_f(30).render("Settings", True, WHITE),
                    _f(30).render("Settings", True, WHITE).get_rect(center=(200, 80)))

        for label, y in [("Sound:", 168), ("Car Color:", 226), ("Difficulty:", 284)]:
            screen.blit(_f(17).render(label, True, GRAY), (40, y))

        sound_btn.text = "ON" if s["sound"] else "OFF"
        color_btn.text = s["car_color"].capitalize()
        diff_btn.text  = s["difficulty"].capitalize()

        for btn in [sound_btn, color_btn, diff_btn, back_btn]:
            btn.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                return s
            if sound_btn.clicked(event):
                s["sound"] = not s["sound"]
            if color_btn.clicked(event):
                s["car_color"] = colors[(colors.index(s["car_color"]) + 1) % len(colors)]
            if diff_btn.clicked(event):
                s["difficulty"] = diffs[(diffs.index(s["difficulty"]) + 1) % len(diffs)]
            if back_btn.clicked(event) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return s

        pygame.display.flip()
        clock.tick(60)
