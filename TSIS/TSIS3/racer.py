import pygame
import random
import os
from pygame.locals import *

SW, SH = 400, 600
FPS    = 60
BASE   = os.path.dirname(os.path.abspath(__file__))

LANES  = [110, 200, 290]   # x-centres of the 3 lanes
FINISH = 2000               # distance to finish (metres)

# ── Colors (HUD / power-ups only — road/cars use images) ─────────
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (120, 120, 120)
GOLD   = (212, 175, 55)
RED    = (220,  30,  30)
GREEN  = (30,  200,  60)
ORANGE = (255, 140,   0)
CYAN   = (0,   200, 255)
NITRO_C= (40,  220,  90)
OIL_C  = (30,   30,  70, 180)

DIFF_CFG = {
    "easy":   {"base_speed": 3, "enemy_ms": 1600, "obs_ms": 4000, "pu_ms": 5000},
    "normal": {"base_speed": 5, "enemy_ms": 1100, "obs_ms": 2500, "pu_ms": 6000},
    "hard":   {"base_speed": 7, "enemy_ms":  750, "obs_ms": 1500, "pu_ms": 7000},
}

# ── Image loader (same pattern as Practice 11) ────────────────────

def _load(filename):
    """Load image from same directory as this file."""
    return pygame.image.load(os.path.join(BASE,"assets", filename))

def _load_scaled(filename, size):
    img = _load(filename)
    return pygame.transform.scale(img, size)

# ── Sprites ───────────────────────────────────────────────────────

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image  = _load("Player.png")
        self.rect   = self.image.get_rect(center=(200, 520))
        self.shield = False

    def move(self):
        k = pygame.key.get_pressed()
        if self.rect.left  > 56  and k[K_LEFT]:  self.rect.x -= 5
        if self.rect.right < 344 and k[K_RIGHT]: self.rect.x += 5


class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed, player_rect):
        super().__init__()
        self.image = _load("Enemy.png")
        # Safe spawn: avoid spawning directly above player
        lane = random.choice(LANES)
        for _ in range(10):
            if abs(lane - player_rect.centerx) >= 50:
                break
            lane = random.choice(LANES)
        self.rect  = self.image.get_rect(center=(lane, -self.image.get_height()))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SH:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = _load("Coin.png")
        self.rect  = self.image.get_rect(center=(random.choice(LANES), -20))
        self.value = random.choice([1, 2, 5])
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SH:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    """Oil spill (slowdown) or barrier (lethal) — drawn as shapes over road."""
    def __init__(self, speed):
        super().__init__()
        self.kind = random.choice(["oil", "oil", "barrier"])
        if self.kind == "oil":
            self.image = pygame.Surface((54, 28), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, OIL_C, (0, 0, 54, 28))
        else:
            self.image = pygame.Surface((56, 18))
            self.image.fill((210, 60, 10))
            pygame.draw.rect(self.image, (240, 120, 40), (2, 4, 52, 10), 3)
        self.rect  = self.image.get_rect(center=(random.choice(LANES), -20))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SH:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    COLORS = {"nitro": ORANGE, "shield": CYAN, "repair": GREEN}

    def __init__(self, speed):
        super().__init__()
        self.kind  = random.choice(["nitro", "shield", "repair"])
        color      = self.COLORS[self.kind]
        self.image = pygame.Surface((34, 34), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (17, 17), 17)
        pygame.draw.circle(self.image, WHITE, (17, 17), 17, 2)
        lbl = pygame.font.SysFont("Verdana", 13, bold=True).render(
            self.kind[0].upper(), True, BLACK)
        self.image.blit(lbl, lbl.get_rect(center=(17, 17)))
        self.rect  = self.image.get_rect(center=(random.choice(LANES), -20))
        self.speed = speed
        self._born = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SH or pygame.time.get_ticks() - self._born > 8000:
            self.kill()


class NitroStrip(pygame.sprite.Sprite):
    """Road event: green boost strip crossing all lanes."""
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((290, 14), pygame.SRCALPHA)
        self.image.fill((40, 220, 90, 160))
        for x in range(0, 290, 30):
            pygame.draw.rect(self.image, (20, 160, 50, 200), (x, 0, 14, 14))
        self.rect  = self.image.get_rect(center=(200, -10))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SH:
            self.kill()


# ── Main game function ────────────────────────────────────────────

def run_game(screen, settings, username):
    """Run one round. Returns {"score", "distance", "coins"} or None on ESC."""
    pygame.display.set_caption(f"Racer — {username}")

    cfg      = DIFF_CFG.get(settings.get("difficulty", "normal"), DIFF_CFG["normal"])
    sound_on = settings.get("sound", True)

    crash_snd = None
    if sound_on:
        try:
            crash_snd = pygame.mixer.Sound(os.path.join(BASE,"assets", "crash.wav"))
        except Exception:
            pass

    # Load background once
    background = _load("AnimatedStreet.png")
    bg_y = 0   # scroll offset

    clock     = pygame.time.Clock()
    speed     = cfg["base_speed"]
    score     = 0
    coins_col = 0
    distance  = 0.0
    next_lvl  = 10

    # Power-up state
    active_pu   = None
    pu_end_ms   = 0
    nitro_bonus = 0

    player = Player()

    enemies   = pygame.sprite.Group()
    coins     = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups  = pygame.sprite.Group()
    nitros    = pygame.sprite.Group()

    def _spawn(cls, group, *args):
        s = cls(*args)
        group.add(s)

    EV_ENEMY = USEREVENT + 1
    EV_COIN  = USEREVENT + 2
    EV_OBS   = USEREVENT + 3
    EV_PU    = USEREVENT + 4
    EV_NITRO = USEREVENT + 5
    pygame.time.set_timer(EV_ENEMY,  cfg["enemy_ms"])
    pygame.time.set_timer(EV_COIN,   900)
    pygame.time.set_timer(EV_OBS,    cfg["obs_ms"])
    pygame.time.set_timer(EV_PU,     cfg["pu_ms"])
    pygame.time.set_timer(EV_NITRO,  8000)

    font_small = pygame.font.SysFont("Verdana", 20)
    font_md    = pygame.font.SysFont("Verdana", 22)

    def cur_speed():
        return speed + nitro_bonus

    running = True
    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        # ── Events ───────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                _clear_timers([EV_ENEMY, EV_COIN, EV_OBS, EV_PU, EV_NITRO])
                return None
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                _clear_timers([EV_ENEMY, EV_COIN, EV_OBS, EV_PU, EV_NITRO])
                return None
            if event.type == EV_ENEMY:
                _spawn(Enemy, enemies, cur_speed() * 1.1, player.rect)
            if event.type == EV_COIN and len(coins) < 4:
                _spawn(Coin, coins, cur_speed())
            if event.type == EV_OBS:
                _spawn(Obstacle, obstacles, cur_speed())
            if event.type == EV_PU and len(powerups) == 0:
                _spawn(PowerUp, powerups, cur_speed())
            if event.type == EV_NITRO:
                _spawn(NitroStrip, nitros, cur_speed())

        # ── Nitro expiry ──────────────────────────────────────────
        if active_pu == "nitro" and now > pu_end_ms:
            active_pu   = None
            nitro_bonus = 0

        # ── Update ────────────────────────────────────────────────
        player.move()
        enemies.update()
        coins.update()
        obstacles.update()
        powerups.update()
        nitros.update()

        # Scroll background (same technique as Practice 11)
        bg_y = (bg_y + cur_speed()) % SH
        distance += cur_speed() / 60.0

        # Difficulty scale
        if coins_col >= next_lvl:
            speed    += 0.5
            next_lvl += 10
            new_ms = max(400, cfg["enemy_ms"] - int(speed * 20))
            pygame.time.set_timer(EV_ENEMY, new_ms)

        # ── Collisions ────────────────────────────────────────────
        for c in pygame.sprite.spritecollide(player, coins, True):
            coins_col += c.value
            score     += c.value

        for _ in pygame.sprite.spritecollide(player, nitros, True):
            nitro_bonus = 3
            active_pu   = "nitro"
            pu_end_ms   = now + 3000

        for pu in pygame.sprite.spritecollide(player, powerups, True):
            if pu.kind == "nitro":
                nitro_bonus = 4
                active_pu   = "nitro"
                pu_end_ms   = now + 4000
            elif pu.kind == "shield":
                player.shield = True
                active_pu     = "shield"
            elif pu.kind == "repair":
                score    += 10
                active_pu = None
                if obstacles:
                    min(obstacles, key=lambda o: abs(o.rect.centery - player.rect.centery)).kill()

        for obs in pygame.sprite.spritecollide(player, obstacles, False):
            if obs.kind == "oil":
                obs.kill()
                nitro_bonus = max(nitro_bonus - 2, -2)
            else:
                if player.shield:
                    player.shield = False
                    active_pu = None
                    obs.kill()
                else:
                    running = False

        if pygame.sprite.spritecollideany(player, enemies):
            if player.shield:
                player.shield = False
                active_pu = None
                enemies.empty()
            else:
                running = False

        if not running:
            break

        # ── Draw ──────────────────────────────────────────────────
        # Scrolling background (two copies, like Practice 11)
        screen.blit(background, (0, bg_y - SH))
        screen.blit(background, (0, bg_y))

        # Road entities (depth order: strips → obstacles → coins → power-ups → enemies)
        for spr in [*nitros, *obstacles, *coins, *powerups, *enemies]:
            screen.blit(spr.image, spr.rect)

        # Player + optional shield ring
        screen.blit(player.image, player.rect)
        if player.shield:
            pygame.draw.ellipse(screen, CYAN, player.rect.inflate(14, 14), 3)

        # ── HUD (same style as Practice 11) ───────────────────────
        score_text = font_small.render(f"Score: {score}",          True, BLACK)
        coin_text  = font_small.render(f"Coins: {coins_col}",      True, GOLD)
        speed_text = font_small.render(f"Speed: {cur_speed():.1f}",True, BLACK)
        dist_text  = font_small.render(f"Dist:  {int(distance)}m", True, BLACK)

        screen.blit(score_text, (10, 10))
        screen.blit(speed_text, (10, 32))
        screen.blit(dist_text,  (10, 54))

        coin_rect = coin_text.get_rect(topright=(SW - 10, 10))
        screen.blit(coin_text, coin_rect)

        if active_pu:
            if active_pu == "nitro":
                secs = max(0, (pu_end_ms - now) // 1000)
                txt, col = f"NITRO  {secs}s", ORANGE
            elif active_pu == "shield":
                txt, col = "SHIELD active", CYAN
            else:
                txt, col = "REPAIR used", GREEN
            pu_surf = font_md.render(txt, True, col)
            screen.blit(pu_surf, pu_surf.get_rect(center=(SW // 2, 46)))

        pygame.display.update()

    # ── Crash sequence (same as Practice 11) ──────────────────────
    if crash_snd:
        crash_snd.play()

    screen.fill((255, 0, 0))
    screen.blit(pygame.font.SysFont("Verdana", 60).render("Game Over", True, BLACK), (30, 250))
    pygame.display.update()
    pygame.time.wait(1500)

    _clear_timers([EV_ENEMY, EV_COIN, EV_OBS, EV_PU, EV_NITRO])
    return {"score": score, "distance": int(distance), "coins": coins_col}


def _clear_timers(events):
    for ev in events:
        pygame.time.set_timer(ev, 0)