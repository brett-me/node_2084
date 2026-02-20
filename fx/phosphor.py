from random import uniform
from config.settings import GamePlayConfig, TimingConfig


class PhosphorPulse:
    """controls global bright-green alpha cycling"""

    def __init__(self):
        self.alpha = GamePlayConfig.PHOS_MIN_ALPHA
        self.phase = "up"
        self.timer = 0

    def _new_hold_time(self):
        t = uniform(0.0, 1.0)
        biased = t * t
        return TimingConfig.PHOS_MIN_HOLD + (
            TimingConfig.PHOS_MAX_HOLD - TimingConfig.PHOS_MIN_HOLD
        ) * (1.0 - biased)

    def update(self, dt):
        min_a = GamePlayConfig.PHOS_MIN_ALPHA
        max_a = GamePlayConfig.PHOS_MAX_ALPHA
        fade_time = TimingConfig.PHOS_FADE_TIME

        if self.phase == "up":
            speed = (max_a - min_a) / fade_time
            self.alpha += speed * dt

            if self.alpha >= max_a:
                self.alpha = max_a
                self.phase = "hold"
                self.hold_time = self._new_hold_time()
                self.timer = self.hold_time

        elif self.phase == "hold":
            self.timer -= dt
            if self.timer <= 0:
                self.phase = "down"

        elif self.phase == "down":
            speed = (max_a - min_a) / fade_time
            self.alpha -= speed * dt
            if self.alpha <= min_a:
                self.alpha = min_a
                self.phase = "up"
