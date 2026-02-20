import pygame
from config.settings import TimingConfig
from config.palette import Colour
from states.play import PlayState


class TerminalState:
    """overlay terminal prompts: Y/N confirmation screens"""

    def __init__(self, font):
        self.font = font

        self.active = False
        self.done = False

        self.lines = []
        self.visible = 0

        self.timer = 0.0
        self.waiting_input = False
        self.prompt_index = 0

        self.answers = ["Y", "Y"]
        self.suspicion_delta = 0

        self.post_attach_timer = None
        self.finishing = False

        self.start_truth_sequence()

    def start_truth_sequence(self):
        self.active = True
        self.done = False

        self.prompt_index = 0
        self.answers = ["", ""]
        self.suspicion_delta = 0

        self.finishing = False
        self.post_attach_timer = None

        self._load_prompt(0)

    def _load_prompt(self, idx):
        if idx == 0:
            self.lines = ["CONFIRM:", "YOUR PERCEPTION IS COMPLETE.", "[Y/N]"]
        else:
            self.lines = ["CONFIRM:", "THE SYSTEM PROVIDES.", "[Y/N]"]

        self.visible = 0
        self.timer = TimingConfig.TERMINAL_LINE_DELAY
        self.waiting_input = False

    def handle_event(self, event):
        if not self.active or not self.waiting_input:
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_y:
            self._record_answer("Y")
        elif event.key == pygame.K_n:
            self._record_answer("N")

    def _record_answer(self, yn):
        self.answers[self.prompt_index] = yn

        if self.prompt_index == 1 and yn == "N":
            self.suspicion_delta += 10

        if self.prompt_index == 0:
            self.prompt_index = 1
            self.timer = TimingConfig.TERMINAL_BLOCK_PAUSE
            self.lines = []
            self.visible = 0
            self.waiting_input = False
        else:
            self.lines = ["RESPONSE RECORDED", "SENSORY FIELD ATTACHED"]
            self.visible = 0
            self.timer = TimingConfig.TERMINAL_LINE_DELAY
            self.waiting_input = False
            self.finishing = True
            self.post_attach_timer = None

    def update(self, dt):
        if not self.active or self.done:
            return

        if self.lines == [] and self.prompt_index == 1:
            self.timer -= dt
            if self.timer <= 0:
                self._load_prompt(1)
            return

        if self.visible < len(self.lines):
            self.timer -= dt
            if self.timer <= 0:
                self.visible = min(self.visible + 1, len(self.lines))
                self.timer = TimingConfig.TERMINAL_LINE_DELAY

                if self.visible == len(self.lines) and self.lines[-1] == "[Y/N]":
                    self.waiting_input = True
            return

        if self.finishing and self.visible >= len(self.lines):
            if self.post_attach_timer is None:
                self.post_attach_timer = TimingConfig.POST_ATTACH_PAUSE

            self.post_attach_timer -= dt
            if self.post_attach_timer <= 0:
                self.done = True
                self.active = False

                self.machine.change_state(
                    PlayState(self.font, starting_suspicion=self.suspicion_delta)
                )

    def render(self, screen, x=40, y=60, line_h=28, colour=(0, 255, 70), phosphor_alpha=255):

        if not self.active:
            return

        screen.fill(Colour.BACKGROUND)

        for i in range(self.visible):
            line = self.lines[i]
            col = Colour.phosphor_colour(colour, phosphor_alpha)
            surf = self.font.render(line, True, col)
            screen.blit(surf, (x, y + i * line_h))
