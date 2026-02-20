import pygame
from config.settings import GamePlayConfig, TimingConfig
from config.palette import Colour


class Sensor:
    """infrared cone scanner: pulsing detection + suspicion gain"""

    def __init__(self, origin, length=140, spread=80):
        self.origin = origin
        self.length = length
        self.spread = spread

        self.pulse_time = 0
        self.alpha = 0
        self.fading_in = True

        ox, oy = origin
        self.cone = pygame.Rect(ox, oy - spread // 2, length, spread)

    def update(self, dt, player, suspicion_system):
        self.pulse_time += dt

        fade_speed = GamePlayConfig.MAX_INFRARED_ALPHA / TimingConfig.SENSOR_ON_TIME

        if self.fading_in:
            self.alpha += fade_speed * dt
            if self.alpha >= GamePlayConfig.MAX_INFRARED_ALPHA:
                self.alpha = GamePlayConfig.MAX_INFRARED_ALPHA
                self.fading_in = False
        else:
            self.alpha -= fade_speed * dt
            if self.alpha <= 0:
                self.alpha = 0
                self.fading_in = True

        in_cone = bool(player) and self.cone.colliderect(player.rect)

        if in_cone and self.alpha > GamePlayConfig.SENSOR_DETECTION:
            suspicion_system.increase(GamePlayConfig.SUSPICION_GAIN_RATE * dt)

        return in_cone and self.alpha > GamePlayConfig.SENSOR_DETECTION

    def render(self, screen, draw_cone=True):
        ox, oy = self.origin
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        pygame.draw.circle(
            overlay,
            Colour.SENSOR,
            (ox, oy),
            6,
        )

        if draw_cone:
            tip = (ox, oy)
            left_base = (ox + self.length, oy - self.spread // 2)
            right_base = (ox + self.length, oy + self.spread // 2)

            pygame.draw.polygon(
                overlay,
                (*Colour.SENSOR, int(self.alpha * 0.25)),
                [tip, left_base, right_base],
            )

        screen.blit(overlay, (0, 0))
