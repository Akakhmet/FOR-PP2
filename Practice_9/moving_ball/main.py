import pygame, sys
from ball import Ball
from enemy import Enemy

pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Maze Ball Game")
clock = pygame.time.Clock()

font_big   = pygame.font.Font(None, 64)
font_small = pygame.font.Font(None, 36)

# ── Уровни ──────────────────────────────────────────────────────────────────
LEVELS = [
    {   # Уровень 1 — спокойный
        "walls": [
            pygame.Rect(100,  0, 20, 300), pygame.Rect(100,400, 20, 200),
            pygame.Rect(250,100, 20, 300), pygame.Rect(250,500,350,  20),
            pygame.Rect(400,200, 20, 200), pygame.Rect(550,  0, 20, 400),
            pygame.Rect(700,300, 20, 200),
        ],
        "spikes": [
            pygame.Rect(160, 450, 20, 20),
            pygame.Rect(320, 150, 20, 20),
        ],
        "enemies": [
            Enemy(300, 300, speed=2, direction='h', range_val=100),
        ],
        "goal": pygame.Rect(740, 550, 35, 35),
        "start": (50, 50),
    },
    {   # Уровень 2 — сложнее
        "walls": [
            pygame.Rect(150,  0, 20, 250), pygame.Rect(150,350, 20, 250),
            pygame.Rect(300,100, 20, 400), pygame.Rect(450,  0, 20, 300),
            pygame.Rect(450,400, 20, 200), pygame.Rect(600,200, 20, 300),
            pygame.Rect(300,500,200,  20),
        ],
        "spikes": [
            pygame.Rect(200, 300, 20, 20), pygame.Rect(370, 150, 20, 20),
            pygame.Rect(520, 450, 20, 20), pygame.Rect(660, 100, 20, 20),
        ],
        "enemies": [
            Enemy(170, 100, speed=2, direction='v', range_val=130),
            Enemy(460, 320, speed=3, direction='h', range_val=100),
        ],
        "goal": pygame.Rect(740, 30, 35, 35),
        "start": (50, 550),
    },
]

# ── Состояние игры ────────────────────────────────────────────────────────
STATE_MENU  = "menu"
STATE_GAME  = "game"
STATE_LOSE  = "lose"
STATE_WIN   = "win"

state       = STATE_MENU
level_idx   = 0
lives       = 3
death_timer = 0   # пауза после смерти

def load_level(idx):
    lvl = LEVELS[idx]
    b = Ball(*lvl["start"])
    enemies = [Enemy(e.start_x, e.start_y,
                     e.size, e.speed, e.direction, e.range_val)
               for e in lvl["enemies"]]
    return b, enemies

ball, enemies = load_level(level_idx)

def draw_lives(surf, n):
    for i in range(n):
        pygame.draw.circle(surf, (255, 50, 50), (20 + i * 30, 20), 10)
        pygame.draw.circle(surf, (255,255,255), (20 + i * 30, 20), 10, 2)

def draw_level_label(surf, idx):
    lbl = font_small.render(f"Level {idx+1}", True, (200, 200, 255))
    surf.blit(lbl, (W - lbl.get_width() - 15, 8))

# ── Главный цикл ─────────────────────────────────────────────────────────
while True:
    dt = clock.tick(60)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_q, pygame.K_ESCAPE):
                pygame.quit(); sys.exit()

            if state == STATE_MENU and e.key == pygame.K_SPACE:
                level_idx = 0
                lives     = 3
                ball, enemies = load_level(level_idx)
                state = STATE_GAME

            elif state in (STATE_LOSE, STATE_WIN) and e.key == pygame.K_r:
                level_idx = 0
                lives     = 3
                ball, enemies = load_level(level_idx)
                state = STATE_GAME

    # ── Логика GAME ───────────────────────────────────────────────────────
    if state == STATE_GAME:
        lvl = LEVELS[level_idx]

        # Пауза после смерти
        if death_timer > 0:
            death_timer -= dt
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]   or keys[pygame.K_w]: ball.accelerate( 0, -ball.speed)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: ball.accelerate( 0,  ball.speed)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: ball.accelerate(-ball.speed, 0)
            if keys[pygame.K_RIGHT]or keys[pygame.K_d]: ball.accelerate( ball.speed, 0)

            ball.update(lvl["walls"], W, H)

            # Обновляем врагов
            for enemy in enemies:
                enemy.update()

            # ✅ Проверка столкновений с шипами и врагами
            if ball.check_hazards(lvl["spikes"], enemies):
                lives -= 1
                if lives <= 0:
                    state = STATE_LOSE
                else:
                    ball.reset()
                    death_timer = 800   # 0.8 сек пауза

            # ✅ Проверка победы
            elif ball.check_goal(lvl["goal"]):
                if level_idx + 1 < len(LEVELS):
                    level_idx += 1
                    ball, enemies = load_level(level_idx)
                else:
                    state = STATE_WIN

    # ── Отрисовка ─────────────────────────────────────────────────────────
    screen.fill((15, 15, 35))

    if state == STATE_MENU:
        t1 = font_big.render("MAZE BALL", True, (255, 50, 50))
        t2 = font_small.render("SPACE — начать игру", True, (200, 200, 255))
        t3 = font_small.render("Стрелки / WASD — движение", True, (150, 150, 200))
        screen.blit(t1, (W//2 - t1.get_width()//2, 200))
        screen.blit(t2, (W//2 - t2.get_width()//2, 300))
        screen.blit(t3, (W//2 - t3.get_width()//2, 345))

    elif state == STATE_GAME:
        lvl = LEVELS[level_idx]

        # Стены
        for wall in lvl["walls"]:
            pygame.draw.rect(screen, (40, 40, 90), wall)
            pygame.draw.rect(screen, (70, 70, 130), wall, 1)

        # Шипы — красные треугольники
        for spike in lvl["spikes"]:
            pts = [
                (spike.centerx, spike.top),
                (spike.left,    spike.bottom),
                (spike.right,   spike.bottom),
            ]
            pygame.draw.polygon(screen, (220, 30, 30), pts)

        # Цель — мигающий зелёный
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        green = (int(50 + 150 * pulse), 220, int(50 + 150 * pulse))
        pygame.draw.rect(screen, green, lvl["goal"])
        pygame.draw.rect(screen, (255, 255, 255), lvl["goal"], 2)

        # Враги
        for enemy in enemies:
            enemy.draw(screen)

        # Мяч
        ball.draw(screen)

        # HUD
        draw_lives(screen, lives)
        draw_level_label(screen, level_idx)

        # Вспышка после смерти
        if death_timer > 0:
            alpha = int(180 * (death_timer / 800))
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash.fill((255, 0, 0, alpha))
            screen.blit(flash, (0, 0))

    elif state == STATE_LOSE:
        t1 = font_big.render("GAME OVER", True, (255, 60, 60))
        t2 = font_small.render("R — начать заново", True, (200, 200, 255))
        screen.blit(t1, (W//2 - t1.get_width()//2, 240))
        screen.blit(t2, (W//2 - t2.get_width()//2, 320))

    elif state == STATE_WIN:
        t1 = font_big.render("ТЫ ПОБЕДИЛ!", True, (50, 255, 100))
        t2 = font_small.render("R — сыграть ещё раз", True, (200, 200, 255))
        screen.blit(t1, (W//2 - t1.get_width()//2, 240))
        screen.blit(t2, (W//2 - t2.get_width()//2, 320))

    pygame.display.flip()