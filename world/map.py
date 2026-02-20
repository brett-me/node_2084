import pygame
from config.palette import Colour
from config.grid import GridConfig


class Map:
    """Loads a tile map from CSV and exposes walls + spawn point."""

    def __init__(self, csv_path):
        self.csv_path = csv_path

        self.cols = GridConfig.COLS
        self.rows = GridConfig.ROWS
        self.cell = GridConfig.CELL

        self.offset_x, self.offset_y = GridConfig.offset()

        self.grid = []          # 2D list of tokens
        self.walls = []         # list[pygame.Rect]
        self.spawn_cell = None  # (col, row)

        self._load_csv()
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
                raise ValueError(
                    f"Map col count mismatch on row {r}: expected {self.cols}, got {len(row)}"
                )
            grid.append(row)

            for c, token in enumerate(row):
                if token == "S":
                    self.spawn_cell = (c, r)

        if self.spawn_cell is None:
            raise ValueError("Map missing spawn cell 'S'")

        self.grid = grid

    def _cell_rect(self, c, r):
        x = self.offset_x + c * self.cell
        y = self.offset_y + r * self.cell
        return pygame.Rect(x, y, self.cell, self.cell)

    def _build_walls(self):
        self.walls = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == "#":
                    self.walls.append(self._cell_rect(c, r))

    def get_walls(self):
        return self.walls

    def get_spawn_point(self):
        c, r = self.spawn_cell
        rect = self._cell_rect(c, r)
        # Player is 20x20 currently; your cell is 16.
        # For now: spawn at cell top-left, just like you asked (no extra behaviour changes).
        return rect.x, rect.y

    def render(self, screen, phosphor_alpha):
        col = Colour.phosphor_colour(Colour.BRIGHT_GREEN, phosphor_alpha)
        for wall in self.walls:
            pygame.draw.rect(screen, col, wall)