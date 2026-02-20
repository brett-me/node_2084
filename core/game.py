import pygame

from core.state_machine import StateMachine
from states.boot import BootState
from fx.phosphor import PhosphorPulse


class Game:
    """main controller: loops, state machine and systems"""

    def __init__(self):
        pygame.init()

        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("NODE 2084")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24)

        self.phosphor = PhosphorPulse()

        starting_state = BootState(self.font)

        self.machine = StateMachine(starting_state)
        self.machine.set_game(self)

        self.running = True

    def run(self):
        """main loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.phosphor.update(dt)
            self.handle_events()
            self.machine.update(dt)
            self.machine.render(self.screen)

            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.machine.handle_event(event)
