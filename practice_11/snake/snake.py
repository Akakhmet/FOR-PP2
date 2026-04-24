import random
import sys
import pygame

pygame.init()

# Window settings
CELL_SIZE = 20
COLUMNS = 30
ROWS = 30
HUD_HEIGHT = 60
WIDTH = CELL_SIZE * COLUMNS
HEIGHT = CELL_SIZE * ROWS + HUD_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 100, 0)
RED = (220, 0, 0)
GRAY = (70, 70, 70)
YELLOW = (255, 220, 0)

# Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Practice 11")
clock = pygame.time.Clock()

# Fonts
hud_font = pygame.font.SysFont("Verdana", 22)
game_over_font = pygame.font.SysFont("Verdana", 48)

# Snake
snake = [(10, 10), (9, 10), (8, 10)]
direction = (1, 0)
next_direction = (1, 0)

# Game values
score = 0
level = 1
foods_eaten = 0
base_speed = 8

# 🔥 FOOD SYSTEM (NEW)
food = None
food_value = 1
food_spawn_time = 0
food_lifetime = 5000  # milliseconds

# ---------------- WALLS ----------------
def get_walls(current_level):
    walls = set()

    # Borders
    for x in range(COLUMNS):
        walls.add((x, 0))
        walls.add((x, ROWS - 1))

    for y in range(ROWS):
        walls.add((0, y))
        walls.add((COLUMNS - 1, y))

    # Extra walls
    if current_level >= 2:
        for y in range(6, 24):
            walls.add((15, y))

    if current_level >= 3:
        for x in range(7, 23):
            walls.add((x, 15))

    return walls

# ---------------- FOOD ----------------
def generate_food():
    """Generate food with random value"""
    walls = get_walls(level)
    free_cells = []

    for x in range(1, COLUMNS - 1):
        for y in range(1, ROWS - 1):
            pos = (x, y)
            if pos not in walls and pos not in snake:
                free_cells.append(pos)

    position = random.choice(free_cells)
    value = random.choice([1, 2, 3])  # 🔥 weight

    return position, value

# ---------------- DRAW ----------------
def draw_cell(position, color):
    x, y = position
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE + HUD_HEIGHT, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)

def draw_board():
    screen.fill(BLACK)

    # HUD
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, HUD_HEIGHT))
    screen.blit(hud_font.render(f"Score: {score}", True, WHITE), (15, 15))
    screen.blit(hud_font.render(f"Level: {level}", True, WHITE), (170, 15))
    screen.blit(hud_font.render(f"Speed: {base_speed + level - 1}", True, WHITE), (300, 15))

    # Walls
    for wall in get_walls(level):
        draw_cell(wall, GRAY)

    # Food
    draw_cell(food, YELLOW)

    # 🔥 DRAW FOOD VALUE
    text = hud_font.render(str(food_value), True, BLACK)
    x, y = food
    screen.blit(text, (x * CELL_SIZE + 5, y * CELL_SIZE + HUD_HEIGHT + 2))

    # Snake
    for i, part in enumerate(snake):
        draw_cell(part, GREEN if i == 0 else DARK_GREEN)

# ---------------- LEVEL ----------------
def change_level_if_needed():
    global level
    level = 1 + score // 4

# ---------------- INPUT ----------------
def handle_direction(key):
    global next_direction

    if key == pygame.K_UP and direction != (0, 1):
        next_direction = (0, -1)
    elif key == pygame.K_DOWN and direction != (0, -1):
        next_direction = (0, 1)
    elif key == pygame.K_LEFT and direction != (1, 0):
        next_direction = (-1, 0)
    elif key == pygame.K_RIGHT and direction != (-1, 0):
        next_direction = (1, 0)

# ---------------- MOVE ----------------
def move_snake():
    global direction, score, foods_eaten, food, food_value, food_spawn_time

    direction = next_direction
    head_x, head_y = snake[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)

    # Collisions
    if new_head[0] < 0 or new_head[0] >= COLUMNS:
        return False
    if new_head[1] < 0 or new_head[1] >= ROWS:
        return False
    if new_head in get_walls(level):
        return False
    if new_head in snake:
        return False

    snake.insert(0, new_head)

    # 🍎 EAT FOOD
    if new_head == food:
        score += food_value
        foods_eaten += 1
        change_level_if_needed()

        food, food_value = generate_food()
        food_spawn_time = pygame.time.get_ticks()
    else:
        snake.pop()

    return True

# ---------------- GAME OVER ----------------
def show_game_over():
    screen.fill(BLACK)
    text1 = game_over_font.render("Game Over", True, RED)
    text2 = hud_font.render(f"Score: {score}", True, WHITE)

    screen.blit(text1, (WIDTH // 2 - 120, HEIGHT // 2 - 50))
    screen.blit(text2, (WIDTH // 2 - 80, HEIGHT // 2 + 20))
    pygame.display.flip()
    pygame.time.wait(2000)

# ---------------- INIT ----------------
food, food_value = generate_food()
food_spawn_time = pygame.time.get_ticks()

running = True
alive = True

# ---------------- MAIN LOOP ----------------
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            handle_direction(event.key)

    if alive:
        # ⏳ FOOD TIMER
        current_time = pygame.time.get_ticks()
        if current_time - food_spawn_time > food_lifetime:
            food, food_value = generate_food()
            food_spawn_time = current_time

        alive = move_snake()
        draw_board()
        pygame.display.flip()

        clock.tick(base_speed + level - 1)
    else:
        show_game_over()
        running = False

pygame.quit()
sys.exit()