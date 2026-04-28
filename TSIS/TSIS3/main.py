

import pygame
import sys
import persistence
import ui
from racer import run_game

def main():
    pygame.init()
    pygame.mixer.init()

    screen   = pygame.display.set_mode((400, 600))
    settings = persistence.load_settings()
    username = ""
    result   = None
    state    = "menu"

    while True:
        if state == "menu":
            state = ui.main_menu(screen)

        elif state == "username":
            name = ui.username_screen(screen)
            if name:
                username = name
                state    = "game"
            else:
                state = "menu"

        elif state == "game":
            result = run_game(screen, settings, username)
            if result is None:
                state = "menu"          # ESC pressed — back to menu
            else:
                persistence.save_score(username, result["score"], result["distance"])
                state = "gameover"

        elif state == "gameover":
            state = ui.game_over_screen(screen, result)

        elif state == "leaderboard":
            ui.leaderboard_screen(screen, persistence.load_leaderboard())
            state = "menu"

        elif state == "settings":
            settings = ui.settings_screen(screen, settings)
            persistence.save_settings(settings)
            state = "menu"

        elif state == "quit":
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
