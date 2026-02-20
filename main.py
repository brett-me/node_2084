import pygame
import sys
from core.game import Game


def main():
    Game().run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
