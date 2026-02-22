import pygame


class TaskMessage:
    """
    Boot-style message sequence:
      Phase A: cursor-only
      Phase B: reveal block 1 line-by-line
      Phase C: hold, then clear
      Phase D: cursor-only
      Phase E: reveal block 2 line-by-line
      Phase F: hold, then clear -> done

    Cursor blink runs continuously (like BootState).
    """

    PH_CURSOR_ONLY_1 = 0
    PH_BLOCK_1 = 1
    PH_HOLD_1 = 2
    PH_CLEAR_1 = 3
    PH_CURSOR_ONLY_2 = 4
    PH_BLOCK_2 = 5
    PH_HOLD_2 = 6
    PH_CLEAR_2 = 7
    PH_DONE = 8

    def __init__(
        self,
        font,
        *,
        block1=None,
        block2=None,
        x=32,
        y=16,
        line_h=28,
        cursor_char="_",
        cursor_blink_s=0.50,
        cursor_only_1_s=0.50,
        cursor_only_2_s=0.75,
        line_gap_s=0.75,
        hold_after_block_s=1,
        clear_s=0.1,
    ):
        self.font = font

        self.block1 = block1 or ["COGNITIVE GRID STABLE"]
        self.block2 = block2 or ["LOCAL INTEGRITY RESTORED"]

        self.x = x
        self.y = y
        self.line_h = line_h

        self.cursor_char = cursor_char

        # timing
        self.cursor_blink_s = float(cursor_blink_s)
        self.cursor_only_1_s = float(cursor_only_1_s)
        self.cursor_only_2_s = float(cursor_only_2_s)
        self.line_gap_s = float(line_gap_s)
        self.hold_after_block_s = float(hold_after_block_s)
        self.clear_s = float(clear_s)

        # runtime
        self.active = False
        self.phase = self.PH_DONE
        self.phase_timer = 0.0

        # cursor blink (always runs while active)
        self.cursor_timer = 0.0
        self.cursor_visible = True

        # line reveal
        self.block_lines = []
        self.visible_lines = []
        self.next_line_index = 0
        self.line_timer = 0.0

    @property
    def done(self):
        return self.phase == self.PH_DONE

    def trigger(self):
        self.active = True

        # reset cursor
        self.cursor_timer = 0.0
        self.cursor_visible = True

        # reset line state
        self.visible_lines = []
        self.block_lines = []
        self.next_line_index = 0
        self.line_timer = 0.0

        # start
        self.phase = self.PH_CURSOR_ONLY_1
        self.phase_timer = self.cursor_only_1_s

    def _start_line_block(self, lines):
        self.visible_lines = []
        self.block_lines = list(lines)
        self.next_line_index = 0
        self.line_timer = self.line_gap_s  # wait before first line (Boot feel)

    def update(self, dt):
        if not self.active or self.phase == self.PH_DONE:
            return

        dt = float(dt)

        # cursor blink ALWAYS runs while active (Boot behaviour)
        self.cursor_timer += dt
        if self.cursor_timer >= self.cursor_blink_s:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0

        # ---- phase logic ----
        if self.phase in (self.PH_CURSOR_ONLY_1, self.PH_HOLD_1, self.PH_CLEAR_1,
                          self.PH_CURSOR_ONLY_2, self.PH_HOLD_2, self.PH_CLEAR_2):
            self.phase_timer -= dt
            if self.phase_timer > 0:
                return

            # phase transitions
            if self.phase == self.PH_CURSOR_ONLY_1:
                self.phase = self.PH_BLOCK_1
                self._start_line_block(self.block1)
                return

            if self.phase == self.PH_HOLD_1:
                self.phase = self.PH_CLEAR_1
                self.phase_timer = self.clear_s
                return

            if self.phase == self.PH_CLEAR_1:
                self.visible_lines = []
                self.phase = self.PH_CURSOR_ONLY_2
                self.phase_timer = self.cursor_only_2_s
                return

            if self.phase == self.PH_CURSOR_ONLY_2:
                self.phase = self.PH_BLOCK_2
                self._start_line_block(self.block2)
                return

            if self.phase == self.PH_HOLD_2:
                self.phase = self.PH_CLEAR_2
                self.phase_timer = self.clear_s
                return

            if self.phase == self.PH_CLEAR_2:
                self.visible_lines = []
                self.phase = self.PH_DONE
                self.active = False
                return

        elif self.phase in (self.PH_BLOCK_1, self.PH_BLOCK_2):
            # reveal next line every line_gap_s
            if self.next_line_index < len(self.block_lines):
                self.line_timer -= dt
                if self.line_timer <= 0:
                    self.visible_lines.append(self.block_lines[self.next_line_index])
                    self.next_line_index += 1
                    self.line_timer = self.line_gap_s
            else:
                # finished revealing this block -> hold
                if self.phase == self.PH_BLOCK_1:
                    self.phase = self.PH_HOLD_1
                    self.phase_timer = self.hold_after_block_s
                else:
                    self.phase = self.PH_HOLD_2
                    self.phase_timer = self.hold_after_block_s

    def render(self, screen, colour):
        if not self.active or self.phase == self.PH_DONE:
            return

        # clear phases draw nothing
        if self.phase in (self.PH_CLEAR_1, self.PH_CLEAR_2):
            return

        # draw visible lines
        for i, line in enumerate(self.visible_lines):
            surf = self.font.render(line, True, colour)
            screen.blit(surf, (self.x, self.y + i * self.line_h))

        # draw cursor under the current block (Boot behaviour)
        # cursor appears during cursor-only phases AND while blocks are revealing/holding
        if self.cursor_visible:
            cursor_y = self.y + len(self.visible_lines) * self.line_h
            cursor = self.font.render(self.cursor_char, True, colour)
            screen.blit(cursor, (self.x, cursor_y))