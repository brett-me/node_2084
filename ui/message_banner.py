class MessageSystem:
    """single line clinical banner with start delay & fixed duration"""

    def __init__(self, font, text):
        self.font = font
        self.text = text

        self.active = False
        self._delay = 0
        self._time_left = 0
        self._showing = False

    def trigger(self, delay, duration):
        self.active = True
        self._delay = delay
        self._time_left = duration
        self._showing = False

    def update(self, dt):
        if not self.active:
            return

        if not self._showing:
            self._delay -= dt
            if self._delay <= 0:
                self._showing = True
            return

        self._time_left -= dt
        if self._time_left <= 0:
            self.active = False
            self._showing = False

    def render(self, screen, colour):
        if not self.active or not self._showing:
            return

        surf = self.font.render(self.text, True, colour)
        x = 32
        y = 16

        screen.blit(surf, (x, y))
