import os
import random
import sys
import time
import pygame
from pygame.locals import *

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# 🔥 BASE VALUES
SPEED = 5
SCORE = 0
COINS_COLLECTED = 0
NEXT_SPEED_UP = 10  # каждые 10 монет ускорение

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PLAYER_IMAGE = os.path.join(BASE_DIR, "Player.png")
ENEMY_IMAGE = os.path.join(BASE_DIR, "Enemy.png")
COIN_IMAGE = os.path.join(BASE_DIR, "Coin.png")
BACKGROUND_IMAGE = os.path.join(BASE_DIR, "AnimatedStreet.png")
CRASH_SOUND = os.path.join(BASE_DIR, "crash.wav")

font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)

background = pygame.image.load(BACKGROUND_IMAGE)

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Practice 11")

# ---------------- PLAYER ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(PLAYER_IMAGE)
        self.rect = self.image.get_rect(center=(160, 520))

    def move(self):
        keys = pygame.key.get_pressed()

        if self.rect.left > 45 and keys[K_LEFT]:
            self.rect.move_ip(-5, 0)

        if self.rect.right < SCREEN_WIDTH - 45 and keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

# ---------------- ENEMY ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(ENEMY_IMAGE)
        self.rect = self.image.get_rect(center=(random.randint(70, SCREEN_WIDTH-70), 0))

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(70, SCREEN_WIDTH-70), 0)

# ---------------- COIN ----------------
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(COIN_IMAGE)
        self.rect = self.image.get_rect(center=(random.randint(65, SCREEN_WIDTH-65), -20))

        # 🔥 ВЕС МОНЕТЫ
        self.value = random.choice([1, 2, 5])

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# ---------------- INIT ----------------
P1 = Player()
E1 = Enemy()

enemies = pygame.sprite.Group(E1)
coins = pygame.sprite.Group()
all_sprites = pygame.sprite.Group(P1, E1)

SPAWN_COIN = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_COIN, 800)

# ---------------- FUNCTIONS ----------------
def spawn_coin():
    if random.randint(1, 100) < 50 and len(coins) < 3:
        coin = Coin()
        coins.add(coin)
        all_sprites.add(coin)

def draw_hud():
    score_text = font_small.render(f"Score: {SCORE}", True, BLACK)
    coin_text = font_small.render(f"Coins: {COINS_COLLECTED}", True, GOLD)
    speed_text = font_small.render(f"Speed: {round(SPEED,1)}", True, BLACK)

    DISPLAYSURF.blit(score_text, (10, 10))
    DISPLAYSURF.blit(speed_text, (10, 30))

    rect = coin_text.get_rect()
    rect.topright = (SCREEN_WIDTH-10, 10)
    DISPLAYSURF.blit(coin_text, rect)

# ---------------- GAME LOOP ----------------
while True:
    for event in pygame.event.get():
        if event.type == SPAWN_COIN:
            spawn_coin()

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.blit(background, (0, 0))
    draw_hud()

    for entity in list(all_sprites):
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # 🔥 СБОР МОНЕТ
    collected = pygame.sprite.spritecollide(P1, coins, True)

    for coin in collected:
        COINS_COLLECTED += coin.value
        SCORE += coin.value

    # 🔥 УСКОРЕНИЕ ПО МОНЕТАМ
    if COINS_COLLECTED >= NEXT_SPEED_UP:
        SPEED += 1
        NEXT_SPEED_UP += 10

    # 💥 COLLISION
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound(CRASH_SOUND).play()
        time.sleep(0.5)

        DISPLAYSURF.fill((255, 0, 0))
        DISPLAYSURF.blit(font.render("Game Over", True, BLACK), (30, 220))

        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)