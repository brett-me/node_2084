from config.settings import TimingConfig
from config.palette import Colour
from states.terminal import TerminalState


class BootState:
    """
    BOOT sequence (refined Step 1):
    Phase A: cursor-only (no text)
    Phase B: initialisation block reveals line-by-line
    Phase C: hold, then clear
    Phase D: cursor-only again
    Phase E: notice block reveals line-by-line
    """

    PH_CURSOR_ONLY_1 = 0
    PH_INIT_LINES = 1
    PH_HOLD_INIT = 2
    PH_CURSOR_ONLY_2 = 3
    PH_NOTICE_LINES = 4
    PH_HOLD_NOTICE = 5

    def __init__(self, font):
        self.font = font
        self.machine = None
        self.game = None
        self.use_play_bg = False

        # cursor blink
        self.cursor_timer = 0
        self.cursor_visible = True

        # phase control
        self.phase = self.PH_CURSOR_ONLY_1
        self.phase_timer = TimingConfig.BOOT_CURSOR_ONLY_1

        # line reveal control
        self.line_timer = 0
        self.next_line_index = 0
        self.visible_lines = []

        self.init_lines = [
            "INITIALISING PERCEPTION",
            "NODE ID: 2084.114.7",
            "COGNITIVE SHELL: ACTIVE",
            "PERCEPTION BANDWIDTH: 12% (OPTIMAL)",
            "EMOTIONAL RANGE: SUPPRESSED",
        ]

        self.notice_lines = [
            "NOTICE:",
            "PREVIOUS NODE: 2084.114.6",
            "STATUS: REMOVED",
            "CAUSE: UNSTRUCTURED CURIOSITY",
        ]

        self.sent_to_terminal = False

    def _start_line_block(self, lines):
        self.visible_lines = []
        self.block_lines = lines
        self.next_line_index = 0
        self.line_timer = TimingConfig.BOOT_LINE_GAP

    def update(self, dt):
        # cursor blink always runs
        self.cursor_timer += dt
        if self.cursor_timer >= TimingConfig.BOOT_CURSOR_BLINK:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        # phase handling
        if self.phase in (self.PH_CURSOR_ONLY_1, self.PH_HOLD_INIT, self.PH_CURSOR_ONLY_2):
            self.phase_timer -= dt
            if self.phase_timer <= 0:
                if self.phase == self.PH_CURSOR_ONLY_1:
                    self.phase = self.PH_INIT_LINES
                    self._start_line_block(self.init_lines)

                elif self.phase == self.PH_HOLD_INIT:
                    self.visible_lines = []
                    self.phase = self.PH_CURSOR_ONLY_2
                    self.phase_timer = TimingConfig.BOOT_CURSOR_ONLY_2

                elif self.phase == self.PH_CURSOR_ONLY_2:
                    self.phase = self.PH_NOTICE_LINES
                    self._start_line_block(self.notice_lines)

        elif self.phase in (self.PH_INIT_LINES, self.PH_NOTICE_LINES):
            if self.next_line_index < len(self.block_lines):
                self.line_timer -= dt
                if self.line_timer <= 0:
                    if not self.use_play_bg:
                        self.use_play_bg = True

                    self.visible_lines.append(self.block_lines[self.next_line_index])
                    self.next_line_index += 1
                    self.line_timer = TimingConfig.BOOT_LINE_GAP
            else:
                if self.phase == self.PH_INIT_LINES:
                    self.phase = self.PH_HOLD_INIT
                    self.phase_timer = TimingConfig.BOOT_HOLD_AFTER_BLOCK

                elif self.phase == self.PH_NOTICE_LINES:
                    self.phase = self.PH_HOLD_NOTICE
                    self.phase_timer = TimingConfig.BOOT_HOLD_AFTER_BLOCK

        elif self.phase == self.PH_HOLD_NOTICE:
            self.phase_timer -= dt
            if self.phase_timer <= 0 and not self.sent_to_terminal:
                self.sent_to_terminal = True
                self.machine.change_state(TerminalState(self.font))

    def render(self, screen):
        screen.fill(Colour.BACKGROUND if self.use_play_bg else Colour.BLACK)

        x = 40
        y = 60
        line_h = 28

        for i, line in enumerate(self.visible_lines):
            alpha = int(self.game.phosphor.alpha)
            col = Colour.phosphor_colour(Colour.BRIGHT_GREEN, alpha)
            surf = self.font.render(line, True, col)
            screen.blit(surf, (x, y + i * line_h))

        if self.cursor_visible:
            cursor_y = y + len(self.visible_lines) * line_h
            alpha = int(self.game.phosphor.alpha)
            col = Colour.phosphor_colour(Colour.BRIGHT_GREEN, alpha)
            cursor = self.font.render("_", True, col)
            screen.blit(cursor, (x, cursor_y))
