import pygame


class SingleLineMessage:
    """
    Single line clinical banner with:
      - start delay
      - optional cursor-only intro (Boot-style)
      - fixed duration

    trigger(delay, duration) API stays the same.
    """

    PH_IDLE = 0
    PH_DELAY = 1
    PH_CURSOR = 2
    PH_LINE = 3

    def __init__(
        self,
        font,
        text,
        *,
        x=32,
        y=16,
        cursor_char="_",
        cursor_blink_s=0.5,
        cursor_intro_s=1.0,   # set 0.0 to disable cursor intro
    ):
        self.font = font
        self.text = text

        self.x = x
        self.y = y

        self.cursor_char = cursor_char
        self.cursor_blink_s = float(cursor_blink_s)
        self.cursor_intro_s = float(cursor_intro_s)

        self.active = False
        self.phase = self.PH_IDLE

        self._delay = 0.0
        self._time_left = 0.0
        self._cursor_left = 0.0

        self._cursor_timer = 0.0
        self._cursor_visible = True

    def trigger(self, delay, duration):
        self.active = True
        self.phase = self.PH_DELAY

        self._delay = float(delay)
        self._time_left = float(duration)
        self._cursor_left = float(self.cursor_intro_s)

        self._cursor_timer = 0.0
        self._cursor_visible = True

    def update(self, dt):
        if not self.active or self.phase == self.PH_IDLE:
            return

        dt = float(dt)

        if self.phase == self.PH_DELAY:
            self._delay -= dt
            if self._delay <= 0:
                # go cursor intro if enabled, else go straight to line
                if self._cursor_left > 0:
                    self.phase = self.PH_CURSOR
                else:
                    self.phase = self.PH_LINE
            return

        if self.phase == self.PH_CURSOR:
            # blink
            self._cursor_timer += dt
            if self._cursor_timer >= self.cursor_blink_s:
                self._cursor_visible = not self._cursor_visible
                self._cursor_timer = 0.0

            self._cursor_left -= dt
            if self._cursor_left <= 0:
                self.phase = self.PH_LINE
            return

        if self.phase == self.PH_LINE:
            self._time_left -= dt
            if self._time_left <= 0:
                self.active = False
                self.phase = self.PH_IDLE

    def render(self, screen, colour):
        if not self.active or self.phase == self.PH_IDLE:
            return

        if self.phase == self.PH_CURSOR:
            if not self._cursor_visible:
                return
            surf = self.font.render(self.cursor_char, True, colour)
            screen.blit(surf, (self.x, self.y))
            return

        if self.phase == self.PH_LINE:
            surf = self.font.render(self.text, True, colour)
            screen.blit(surf, (self.x, self.y))