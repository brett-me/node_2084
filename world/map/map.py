
import pygame
from config.palette import Colour
from config.grid import GridConfig
from world.map.markers import parse_markers
from world.map.debug_draw import draw_markers

class Map:
    """Loads a tile map from CSV and exposes walls + markers."""

    def __init__(self, csv_path):
        self.csv_path = csv_path

        self.cols = GridConfig.COLS
        self.rows = GridConfig.ROWS
        self.cell = GridConfig.CELL
        self.offset_x, self.offset_y = GridConfig.offset()

        self.grid = []
        self.walls = []

        self.marker_data = None
        self.debug_draw_markers = True  # toggle

        self._load_csv()
        self.marker_data = parse_markers(self.grid)

        if self.marker_data["spawn_cell"] is None:
            raise ValueError("Map missing spawn cell 'S'")

        self._build_walls()

    def _load_csv(self):
        with open(self.csv_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]

        if len(lines) != self.rows:
            raise ValueError(f"Map row count mismatch: expected {self.rows}, got {len(lines)}")

        grid = []
        for r, line in enumerate(lines):
            row = [c.strip() for c in line.split(",")]
            if len(row) != self.cols:
                raise ValueError(f"Map col count mismatch on row {r}: expected {self.cols}, got {len(row)}")
            grid.append(row)

        self.grid = grid

    def cell_rect(self, c, r):
        x = self.offset_x + c * self.cell
        y = self.offset_y + r * self.cell
        return pygame.Rect(x, y, self.cell, self.cell)

    def cell_to_world(self, c, r, centre=False):
        rect = self.cell_rect(c, r)
        if centre:
            return rect.centerx, rect.centery
        return rect.x, rect.y

    def _build_walls(self):
        self.walls = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == "#":
                    self.walls.append(self.cell_rect(c, r))

    def get_walls(self):
        return self.walls

    def get_spawn_point(self):
        c, r = self.marker_data["spawn_cell"]
        x, y = self.cell_to_world(c, r, centre=False)
        return x, y

    def render(self, screen, phosphor_alpha):
        # walls
        col = Colour.phosphor_colour(Colour.BRIGHT_GREEN, phosphor_alpha)
        for wall in self.walls:
            pygame.draw.rect(screen, col, wall)

        # debug overlays (optional)
        if self.debug_draw_markers:
            draw_markers(screen, self, phosphor_alpha)