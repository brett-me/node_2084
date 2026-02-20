# world/map.py

import pygame

from config.palette import Colour
from world.sensors import Sensor


class Map:
    """
    Owns on-screen geometry (walls) and exposes spawn points + sensor placement.

    Notes:
    - The map is the whole screen (no scrolling).
    - Layouts can mutate later via cycle/phase logic.
    """

    def __init__(self, layout_id="corridor_v1", offset_y=100):
        self.layout_id = layout_id
        self.offset_y = offset_y

        self.walls = []
        self._spawn_point = (0, 0)
        self._sensor_specs = []

        self._build_layout()

    def _build_layout(self):
        oy = self.offset_y

        # Corridor v1: three rects (top/bottom rails + left block).
        # These numbers are your current prototype layout.
        left_x = 100
        top_y = 200 + oy
        width = 600
        rail_h = 20
        gap_h = 100

        self.walls = [
            pygame.Rect(left_x, top_y, width, rail_h),                     # top rail
            pygame.Rect(left_x, top_y + gap_h, width, rail_h),             # bottom rail
            pygame.Rect(left_x, top_y, rail_h, gap_h),                     # left block
        ]

        # Spawn point: inside corridor, slightly right of the left block, vertically centred.
        self._spawn_point = (140, top_y + (gap_h // 2))

        # Sensor specs: list of dicts so multiple sensors can exist later.
        # For now: one sensor, matching your current prototype.
        self._sensor_specs = [
            {"origin": (114, 360), "length": 584, "spread": 72},
        ]

    def get_walls(self):
        return self.walls

    def get_spawn_point(self):
        return self._spawn_point

    def create_sensors(self):
        """Instantiate sensors for the current layout."""
        sensors = []
        for spec in self._sensor_specs:
            sensors.append(
                Sensor(
                    origin=spec["origin"],
                    length=spec.get("length", 140),
                    spread=spec.get("spread", 80),
                )
            )
        return sensors

    def render(self, screen, phosphor_alpha):
        col = Colour.phosphor_colour(Colour.BRIGHT_GREEN, phosphor_alpha)
        for wall in self.walls:
            pygame.draw.rect(screen, col, wall)
