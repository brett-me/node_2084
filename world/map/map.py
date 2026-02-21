import pygame
from config.palette import Colour
from config.grid import GridConfig
from utils.paths import asset_path


class Map:
    """Loads tile map from CSV. Owns static walls, dynamic wall groups, and trigger cells."""

    STATIC_WALL = "#"
    SPAWN = "S"

    # dynamic wall groups (inactive unless toggled)
    DYNAMIC_WALL_TOKENS = {"!", "@", "%", "*", "$"}

    # trigger cells (cause toggles)
    TRIGGER_TOKENS = {"T", "U", "V", "W"}

    def __init__(self, csv_filename):
        self.csv_path = asset_path(csv_filename)

        self.cols = GridConfig.COLS
        self.rows = GridConfig.ROWS
        self.cell = GridConfig.CELL
        self.offset_x, self.offset_y = GridConfig.offset()

        self.grid = []
        self.spawn_cell = None

        self.static_walls = []
        self.dynamic_cells = {tok: [] for tok in self.DYNAMIC_WALL_TOKENS}
        self.dynamic_active = {tok: False for tok in self.DYNAMIC_WALL_TOKENS}

        self.triggers = {tok: set() for tok in self.TRIGGER_TOKENS}

        self._load_csv()
        self._build_static_walls()

    def _load_csv(self):
        with open(self.csv_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]

        if len(lines) != self.rows:
            raise ValueError(f"Map row mismatch: expected {self.rows}, got {len(lines)}")

        grid = []
        for r, line in enumerate(lines):
            row = [c.strip() for c in line.split(",")]
            if len(row) != self.cols:
                raise ValueError(f"Map col mismatch on row {r}: expected {self.cols}, got {len(row)}")

            for c, token in enumerate(row):
                if token == self.SPAWN:
                    self.spawn_cell = (c, r)

                if token in self.DYNAMIC_WALL_TOKENS:
                    self.dynamic_cells[token].append((c, r))

                if token in self.TRIGGER_TOKENS:
                    self.triggers[token].add((c, r))

            grid.append(row)

        if self.spawn_cell is None:
            raise ValueError("Map missing spawn cell 'S'")

        self.grid = grid

    def _cell_rect(self, c, r):
        x = self.offset_x + c * self.cell
        y = self.offset_y + r * self.cell
        return pygame.Rect(x, y, self.cell, self.cell)

    def _build_static_walls(self):
        self.static_walls = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == self.STATIC_WALL:
                    self.static_walls.append(self._cell_rect(c, r))

    def get_spawn_point(self):
        c, r = self.spawn_cell
        rect = self._cell_rect(c, r)
        return rect.x, rect.y

    def world_to_cell(self, x, y):
        """Convert world pixel coords to (col,row) inside the grid; returns None if outside."""
        gx = x - self.offset_x
        gy = y - self.offset_y
        if gx < 0 or gy < 0:
            return None
        c = int(gx // self.cell)
        r = int(gy // self.cell)
        if c < 0 or c >= self.cols or r < 0 or r >= self.rows:
            return None
        return (c, r)

    def is_trigger(self, cell, trigger_token):
        if cell is None:
            return False
        return cell in self.triggers.get(trigger_token, set())

    def set_group_active(self, wall_token, active=True):
        if wall_token not in self.DYNAMIC_WALL_TOKENS:
            return
        self.dynamic_active[wall_token] = bool(active)

    def get_walls(self):
        walls = list(self.static_walls)
        for tok, active in self.dynamic_active.items():
            if not active:
                continue
            for (c, r) in self.dynamic_cells[tok]:
                walls.append(self._cell_rect(c, r))
        return walls

    def render(self, screen, phosphor_alpha, draw_dynamic_walls=True):
        col = Colour.phosphor_colour(Colour.BRIGHT_GREEN, phosphor_alpha)

        for wall in self.static_walls:
            pygame.draw.rect(screen, col, wall)

        if draw_dynamic_walls:
            for tok, active in self.dynamic_active.items():
                if not active:
                    continue
                for (c, r) in self.dynamic_cells[tok]:
                    pygame.draw.rect(screen, col, self._cell_rect(c, r))