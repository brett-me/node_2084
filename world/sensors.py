import pygame
from config.settings import TimingConfig, GamePlayConfig
from config.palette import Colour


class Sensor:
    """
    Grid sensor (staggered wake):
    - emitter always drawn
    - cone is 5 parallel rays (cells)
    - rays stop when they hit map occluders
    - sensor is "disabled" until the player first steps into its line-of-sight cells
    - once enabled, it pulses and can increase suspicion
    """

    def __init__(self, cell, direction_token, max_length_cells=30):
        self.cell = cell                  # (c, r)
        self.dir = direction_token        # "^", "v", "<", ">"
        self.max_len = max_length_cells

        # pulse state (only used once enabled)
        self.alpha = 0.0
        self.fading_in = True

        # activation latch
        self.enabled = False  # becomes True once player enters LOS once

        # cached ray data
        self._ray_cells = set()
        self._ray_endpoints = []

    # ---- direction helpers ----

    def _forward(self):
        if self.dir == "^":
            return (0, -1)
        if self.dir == "v":
            return (0, 1)
        if self.dir == "<":
            return (-1, 0)
        return (1, 0)

    def _perp(self):
        fx, _ = self._forward()
        return (1, 0) if fx == 0 else (0, 1)

    def _pulse(self, dt):
        fade_speed = GamePlayConfig.MAX_INFRARED_ALPHA / TimingConfig.SENSOR_ON_TIME

        if self.fading_in:
            self.alpha += fade_speed * dt
            if self.alpha >= GamePlayConfig.MAX_INFRARED_ALPHA:
                self.alpha = float(GamePlayConfig.MAX_INFRARED_ALPHA)
                self.fading_in = False
        else:
            self.alpha -= fade_speed * dt
            if self.alpha <= 0:
                self.alpha = 0.0
                self.fading_in = True

    # ---- ray casting ----

    def _cast_rays(self, game_map, occlusion_behaviour="B"):
        self._ray_cells.clear()
        self._ray_endpoints.clear()

        fx, fy = self._forward()
        px, py = self._perp()

        base_c, base_r = self.cell

        for offset in (-2, -1, 0, 1, 2):
            start = (base_c + px * offset, base_r + py * offset)

            if not game_map.in_bounds(start):
                continue

            current = start
            last_free = start

            for _ in range(self.max_len):
                nxt = (current[0] + fx, current[1] + fy)

                if not game_map.in_bounds(nxt):
                    break

                if game_map.is_sensor_occluder(nxt, behaviour=occlusion_behaviour):
                    break

                current = nxt
                last_free = current
                self._ray_cells.add(current)

            end_x, end_y = game_map.cell_center(last_free)
            self._ray_endpoints.append((end_x, end_y))

    # ---- public API ----

    def update(self, dt, game_map, player, suspicion_system):
        """
        Returns True if player detected (i.e. enabled + alpha high + player in ray cells).
        """

        # Always cast rays so we can "wake" based on LOS
        self._cast_rays(game_map, occlusion_behaviour="B")

        if not player:
            return False

        player_cell = game_map.world_to_cell(player.rect.centerx, player.rect.centery)

        # Wake logic: first time player steps into this sensor's LOS
        if (not self.enabled) and (player_cell in self._ray_cells):
            self.enabled = True
            # start from dark so the first ramp feels deliberate
            self.alpha = 0.0
            self.fading_in = True

        # If not enabled yet: no pulse, no detection, no suspicion
        if not self.enabled:
            return False

        # Enabled: pulse + detect
        self._pulse(dt)

        if self.alpha <= GamePlayConfig.SENSOR_DETECTION:
            return False

        detected = player_cell in self._ray_cells
        if detected:
            suspicion_system.increase(GamePlayConfig.SUSPICION_GAIN_RATE * dt)

        return detected

    def render(self, screen, game_map, draw_cone=True):
        ox, oy = game_map.cell_center(self.cell)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        # emitter always visible
        pygame.draw.circle(overlay, Colour.SENSOR, (ox, oy), 6)

        # cone only if enabled (and we have endpoints)
        if draw_cone and self.enabled and self._ray_endpoints:
            points = [(ox, oy)] + self._ray_endpoints + [(ox, oy)]
            a = int(self.alpha * 0.25)
            pygame.draw.polygon(overlay, (*Colour.SENSOR, a), points)

        screen.blit(overlay, (0, 0))