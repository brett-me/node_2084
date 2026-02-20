import pygame
from config.palette import Colour


class Map:
    """Owns on-screen geometry (walls) and can mutate later by cycle."""

    def __init__(self, layout_id="corridor_v1", offset_y=100):
        self.layout_id = layout_id
        self.offset_y = offset_y
        self.walls = self._build_layout()

    def _build_layout(self):
        oy = self.offset_y
        walls = []
        walls.append(pygame.Rect(100, 200 + oy, 600, 20))  # top
        walls.append(pygame.Rect(100, 300 + oy, 600, 20))  # bottom
        walls.append(pygame.Rect(100, 200 + oy, 20, 100))  # left block
        return walls

    def get_walls(self):
        return self.walls

    def get_spawn_points(self):
        return (140, 250 + self.offset_y)

    def render(self, screen, phosphor_alpha):
        col = Colour.phosphor_colour(Colour.BRIGHT_GREEN, phosphor_alpha)
        for wall in self.walls:
            pygame.draw.rect(screen, col, wall)
