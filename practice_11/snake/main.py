#!/usr/bin/env python3
"""
Snake Game — Pygame Extended Version (TSIS 2 Upgrade, Modular)
Entry point and main game loop.
"""
import pygame
import sys

from settings import (
    WIDTH, HEIGHT, HUD_HEIGHT, BASE_FPS, FPS_STEP, MAX_FPS,
    FOOD_PER_LEVEL, MAX_FOODS, SPAWN_INTERVAL,
    STATE_START, STATE_RUNNING, STATE_PAUSED, STATE_DEAD,
    KEY_START, KEY_PAUSE, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
)
from utils import draw_hud, draw_overlay, draw_background_grid, draw_walls
from food import FoodItem, spawn_food, draw_legend
from snake import Snake


def handle_input(snake, state):
    """Process pygame events, return state change or None."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type == pygame.KEYDOWN:
            if event.key in KEY_START:
                if state in (STATE_START, STATE_DEAD):
                    return "RESET"
                elif state == STATE_PAUSED:
                    return STATE_RUNNING

            if event.key == KEY_PAUSE:
                if state == STATE_RUNNING:
                    return STATE_PAUSED
                elif state == STATE_PAUSED:
                    return STATE_RUNNING

            if event.key in KEY_UP:
                snake.set_direction((0, -1))
            elif event.key in KEY_DOWN:
                snake.set_direction((0, 1))
            elif event.key in KEY_LEFT:
                snake.set_direction((-1, 0))
            elif event.key in KEY_RIGHT:
                snake.set_direction((1, 0))

    return None


def run_game():
    """Main game execution loop."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT + HUD_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    # Game state
    snake = Snake()
    foods = []
    first = spawn_food(snake.body, foods)
    if first:
        foods.append(first)

    score = 0
    level = 1
    food_eaten = 0
    current_fps = BASE_FPS
    spawn_timer = 0.0
    state = STATE_START

    while True:
        # Delta-time for real-time timers (independent of FPS)
        dt = clock.tick(current_fps) / 1000.0

        # ── Input ────────────────────────────────────────────────
        input_result = handle_input(snake, state)
        if input_result == "QUIT":
            pygame.quit()
            sys.exit()
        elif input_result == "RESET":
            snake.reset()
            foods = []
            first = spawn_food(snake.body, foods)
            if first:
                foods.append(first)
            score = level = food_eaten = 0
            current_fps = BASE_FPS
            spawn_timer = 0.0
            state = STATE_RUNNING
        elif input_result in (STATE_RUNNING, STATE_PAUSED):
            state = input_result

        # ── Logic (only when RUNNING) ───────────────────────────
        if state == STATE_RUNNING:
            snake.apply_direction()
            head = snake.head
            new_head = (head[0] + snake.direction[0], head[1] + snake.direction[1])

            # Collision checks
            if snake.check_wall_collision(new_head) or snake.check_self_collision(new_head):
                state = STATE_DEAD
            else:
                # Move snake: insert new head
                snake.body.insert(0, new_head)

                # Check for food collision
                eaten = None
                for f in foods:
                    if f.pos == new_head:
                        eaten = f
                        break

                if eaten:
                    # 🍎 Food eaten: award points, grow snake
                    score += eaten.points * level
                    food_eaten += 1

                    # Grow: already kept tail (+1), add extra if grow > 1
                    if eaten.grow > 1:
                        snake.grow_by(eaten.grow - 1)

                    foods.remove(eaten)

                    # Level up?
                    if food_eaten >= FOOD_PER_LEVEL:
                        level += 1
                        food_eaten = 0
                        current_fps = min(MAX_FPS, BASE_FPS + (level - 1) * FPS_STEP)

                    # Spawn replacement immediately
                    replacement = spawn_food(snake.body, foods)
                    if replacement:
                        foods.append(replacement)
                else:
                    # No food: remove tail to maintain length
                    snake.body.pop()

                # Update food timers
                for f in foods[:]:
                    if f.update(dt):
                        foods.remove(f)

                # Periodic auto-spawn
                spawn_timer += dt
                if spawn_timer >= SPAWN_INTERVAL and len(foods) < MAX_FOODS:
                    spawn_timer = 0.0
                    extra = spawn_food(snake.body, foods)
                    if extra:
                        foods.append(extra)

        # ── Rendering ────────────────────────────────────────────
        screen.fill((0, 0, 0))
        draw_background_grid(screen)
        draw_walls(screen)

        for f in foods:
            f.draw(screen)

        snake.draw(screen)
        draw_hud(screen, score, level, current_fps)
        draw_legend(screen)

        # Overlays
        if state == STATE_START:
            draw_overlay(screen, "SNAKE", "SPACE to start  |  WASD/Arrows  |  P = pause")
        elif state == STATE_PAUSED:
            draw_overlay(screen, "PAUSED", "Press P or SPACE to resume")
        elif state == STATE_DEAD:
            draw_overlay(screen, "GAME OVER", f"Score: {score}  Level: {level}  |  SPACE to restart")

        pygame.display.flip()


if __name__ == "__main__":
    run_game()