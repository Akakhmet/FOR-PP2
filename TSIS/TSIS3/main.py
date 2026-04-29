import pygame
import sys
import persistence   
import ui            
from racer import run_game  # main game loop

def main():
    pygame.init()
    pygame.mixer.init()

    # create the game window
    screen = pygame.display.set_mode((400, 600))

    # load saved settings
    settings = persistence.load_settings()

    username = ""    # player's name
    result   = None  # game result (score, distance)
    state    = "menu"  # current screen/state

    # main loop
    while True:

        #MAIN MENU
        if state == "menu":
            state = ui.main_menu(screen)

        #USERNAME INPUT
        elif state == "username":
            name = ui.username_screen(screen)
            if name:
                username = name
                state = "game"
            else:
                # if user cancels, go back to menu
                state = "menu"

        #GAMEPLAY
        elif state == "game":
            result = run_game(screen, settings, username)

            if result is None:
                # player pressed ESC → return to menu
                state = "menu"
            else:
                # save player's score after the game ends
                persistence.save_score(
                    username,
                    result["score"],
                    result["distance"]
                )
                state = "gameover"

        #GAME OVER SCREEN
        elif state == "gameover":
            state = ui.game_over_screen(screen, result)

        # ===== LEADERBOARD =====
        elif state == "leaderboard":
            ui.leaderboard_screen(
                screen,
                persistence.load_leaderboard()
            )
            state = "menu"

        #SETTINGS
        elif state == "settings":
            settings = ui.settings_screen(screen, settings)
            persistence.save_settings(settings)
            state = "menu"

        
        elif state == "quit":
            pygame.quit()
            sys.exit()


# entry point of the program
if __name__ == "__main__":
    main()