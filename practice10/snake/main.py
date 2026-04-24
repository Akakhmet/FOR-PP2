#!/usr/bin/env python3
"""
Snake Game — Pygame Extended Version (Modular)
Entry point and main game loop.
"""
import pygame
import sys

from settings import (
    WIDTH, HEIGHT, HUD_HEIGHT, BASE_FPS, FPS_STEP, MAX_FPS,
    FOOD_PER_LEVEL, STATE_START, STATE_RUNNING, STATE_PAUSED, STATE_DEAD,
    KEY_START, KEY_PAUSE, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
)
from utils import draw_hud, draw_overlay, draw_background_grid, draw_walls
from food import random_food, draw_food
from snake import Snake


def handle_input(snake, state):
    """Process pygame events, return new state or None if unchanged."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type == pygame.KEYDOWN:
            # Start / Restart / Unpause
            if event.key in KEY_START:
                if state in (STATE_START, STATE_DEAD):
                    return "RESET"
                elif state == STATE_PAUSED:
                    return STATE_RUNNING

            # Pause toggle
            if event.key == KEY_PAUSE:
                if state == STATE_RUNNING:
                    return STATE_PAUSED
                elif state == STATE_PAUSED:
                    return STATE_RUNNING

            # Direction input
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
    food = random_food(snake.body)
    score = 0
    level = 1
    food_eaten = 0
    current_fps = BASE_FPS
    state = STATE_START

    while True:
        # ── Input ────────────────────────────────────────────────
        input_result = handle_input(snake, state)
        if input_result == "QUIT":
            pygame.quit()
            sys.exit()
        elif input_result == "RESET":
            snake.reset()
            food = random_food(snake.body)
            score = 0
            level = 1
            food_eaten = 0
            current_fps = BASE_FPS
            state = STATE_RUNNING
        elif input_result in (STATE_RUNNING, STATE_PAUSED):
            state = input_result

        # ── Logic (only when RUNNING) ───────────────────────────
        if state == STATE_RUNNING:
            snake.apply_direction()

            # Calculate new head position
            head = snake.head
            new_head = (head[0] + snake.direction[0], head[1] + snake.direction[1])

            # Collision checks
            if snake.check_wall_collision(new_head) or snake.check_self_collision(new_head):
                state = STATE_DEAD
            else:
                # 1. Добавляем новую голову
                snake.body.insert(0, new_head)

                # 2. Проверяем, съели ли еду
                if new_head == food:
                    # 🍎 Еда съедена: хвост НЕ удаляем → змея растёт
                    food_eaten += 1
                    score += 10 * level

                    if food_eaten >= FOOD_PER_LEVEL:
                        level += 1
                        food_eaten = 0
                        current_fps = min(MAX_FPS, BASE_FPS + (level - 1) * FPS_STEP)

                    food = random_food(snake.body)  # новая еда
                else:
                    # 🚫 Еда не съедена: удаляем хвост → длина сохраняется
                    snake.body.pop()

        # ── Rendering ────────────────────────────────────────────
        screen.fill((0, 0, 0))
        draw_background_grid(screen)
        draw_walls(screen)
        draw_food(screen, food)
        snake.draw(screen)
        draw_hud(screen, score, level, current_fps)

        # Overlays
        if state == STATE_START:
            draw_overlay(screen, "SNAKE", "Press SPACE or ENTER to start  |  WASD / Arrows")
        elif state == STATE_PAUSED:
            draw_overlay(screen, "PAUSED", "Press P or SPACE to resume")
        elif state == STATE_DEAD:
            draw_overlay(screen, "GAME OVER", f"Score: {score}   Level: {level}   |   SPACE to restart")

        pygame.display.flip()
        clock.tick(current_fps)


if __name__ == "__main__":
    run_game()