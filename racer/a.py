import pygame
import random
import sys
import time

pygame.init()

# ---------------------------------
# Game settings
# ---------------------------------
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Road limits
ROAD_LEFT = 50
ROAD_RIGHT = 350
ROAD_MARGIN = 5

# Object sizes
CAR_WIDTH = 40
CAR_HEIGHT = 70
COIN_SIZE = 24

# Speed of game objects
SPEED = 5
PLAYER_SPEED = 5

# Scores
SCORE = 0
COINS_COLLECTED = 0

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 120, 255)
GRAY = (70, 70, 70)
YELLOW = (255, 215, 0)
ROAD_LINE = (240, 240, 240)

# Create display
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")

# Fonts
font_big = pygame.font.SysFont("Verdana", 50)
font_small = pygame.font.SysFont("Verdana", 20)
game_over_text = font_big.render("Game Over", True, BLACK)

# FPS controller
FramePerSec = pygame.time.Clock()

# Custom event for increasing speed
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)


# ---------------------------------
# Helper function
# ---------------------------------
def random_road_x(object_width):
    half_width = object_width // 2

    return random.randint(
        ROAD_LEFT + ROAD_MARGIN + half_width,
        ROAD_RIGHT - ROAD_MARGIN - half_width
    )


# ---------------------------------
# Function to draw road background
# ---------------------------------
def draw_road(surface, line_offset):
    # Fill whole screen with green grass
    surface.fill(GREEN)

    # Draw gray road in the middle
    pygame.draw.rect(
        surface,
        GRAY,
        (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_HEIGHT)
    )

    # Draw road borders
    pygame.draw.line(surface, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, SCREEN_HEIGHT), 4)
    pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_HEIGHT), 4)

    # Draw moving dashed line in the center
    for y in range(-40, SCREEN_HEIGHT, 80):
        pygame.draw.rect(surface, ROAD_LINE, (192, y + line_offset, 16, 40))


# ---------------------------------
# Enemy class
# ---------------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Create enemy car surface
        self.image = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)

        # Draw enemy body
        pygame.draw.rect(
            self.image,
            RED,
            (0, 0, CAR_WIDTH, CAR_HEIGHT),
            border_radius=8
        )

        # Draw windows
        pygame.draw.rect(self.image, BLACK, (8, 10, 24, 18), border_radius=4)

        # Draw wheels
        pygame.draw.circle(self.image, BLACK, (6, 15), 5)
        pygame.draw.circle(self.image, BLACK, (34, 15), 5)
        pygame.draw.circle(self.image, BLACK, (6, 55), 5)
        pygame.draw.circle(self.image, BLACK, (34, 55), 5)

        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        self.rect.center = (
            random_road_x(CAR_WIDTH),
            random.randint(-300, -80)
        )

    def move(self):
        global SCORE

        # Move enemy downward
        self.rect.move_ip(0, SPEED)

        # If enemy leaves screen, send it back to top
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset_position()


# ---------------------------------
# Player class
# ---------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Create player car surface
        self.image = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)

        # Draw player body
        pygame.draw.rect(
            self.image,
            BLUE,
            (0, 0, CAR_WIDTH, CAR_HEIGHT),
            border_radius=8
        )

        # Draw windows
        pygame.draw.rect(self.image, BLACK, (8, 10, 24, 18), border_radius=4)

        # Draw wheels
        pygame.draw.circle(self.image, BLACK, (6, 15), 5)
        pygame.draw.circle(self.image, BLACK, (34, 15), 5)
        pygame.draw.circle(self.image, BLACK, (6, 55), 5)
        pygame.draw.circle(self.image, BLACK, (34, 55), 5)

        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        # Move left if player is still inside the road
        if pressed_keys[pygame.K_LEFT] and self.rect.left > ROAD_LEFT + ROAD_MARGIN:
            self.rect.move_ip(-PLAYER_SPEED, 0)

        # Move right if player is still inside the road
        if pressed_keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT - ROAD_MARGIN:
            self.rect.move_ip(PLAYER_SPEED, 0)


# ---------------------------------
# Coin class
# ---------------------------------
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Create coin surface
        self.image = pygame.Surface((COIN_SIZE, COIN_SIZE), pygame.SRCALPHA)

        # Draw coin
        pygame.draw.circle(self.image, YELLOW, (12, 12), 12)
        pygame.draw.circle(self.image, BLACK, (12, 12), 12, 2)

        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        # Put coin at random position above screen
        self.rect.center = (
            random_road_x(COIN_SIZE),
            random.randint(-500, -50)
        )

    def move(self):
        # Move coin downward
        self.rect.move_ip(0, SPEED)

        # If coin leaves screen, respawn it
        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position()


# Create objects
P1 = Player()
E1 = Enemy()
E2 = Enemy()
C1 = Coin()

# Create groups
enemies = pygame.sprite.Group()
enemies.add(E1)
enemies.add(E2)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(E2)
all_sprites.add(C1)

# Offset for moving road lines
line_offset = 0


# ---------------------------------
# Main game loop
# ---------------------------------
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 1

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Draw road background
    draw_road(DISPLAYSURF, line_offset)

    # Animate road center lines
    line_offset += SPEED
    if line_offset >= 80:
        line_offset = 0

    # Show score text
    score_text = font_small.render("Score: " + str(SCORE), True, BLACK)
    coin_text = font_small.render("Coins: " + str(COINS_COLLECTED), True, BLACK)

    # Top-left
    DISPLAYSURF.blit(score_text, (10, 10))

    # Top-right
    DISPLAYSURF.blit(coin_text, (SCREEN_WIDTH - coin_text.get_width() - 10, 10))

    # Draw and move all sprites
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Check if player collects coin
    collected = pygame.sprite.spritecollide(P1, coins, False)
    if collected:
        COINS_COLLECTED += 1
        C1.reset_position()

    # Check collision with enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        time.sleep(0.3)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_text, (60, 250))
        pygame.display.update()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)