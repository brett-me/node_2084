import pygame
from config.palette import Colour
from config.grid import GridConfig


class Map:
    """
    Loads a tile map from CSV and exposes:
    - walls (permanent)
    - spawn point
    - task zones, discovery zones, anomalies
    - sensor spawns (pos + direction)
    - dynamic wall cells (future behaviour)
    """

    # symbols
    WALL = "#"
    SPAWN = "S"

    # dynamic wall markers (behaviour later)
    FUTURE_WALL = "!"   # open space that becomes wall once past
    TOGGLE_WALL = "?"   # wall that opens/closes when near

    # sensors
    SENSOR_UP = "^"
    SENSOR_DOWN = "v"
    SENSOR_LEFT = "<"
    SENSOR_RIGHT = ">"

    # tasks / cycle zones
    TASKS_CYCLE_1 = set(["A", "B", "C", "D"])
    TASKS_CYCLE_2 = set(["a", "b", "c", "d"])

    # discoveries
    DISCOVERIES_CYCLE_2 = set(["x", "y", "z"])
    # (you mentioned lower-case letters represent cycle 2 spawns generally;
    # if you add lower-case discovery markers later we can extend similarly)

    # anomalies
    ANOMALIES_CYCLE_1 = set(["o", "p"])

    def __init__(self, csv_path):
        self.csv_path = csv_path

        self.cols = GridConfig.COLS
        self.rows = GridConfig.ROWS
        self.cell = GridConfig.CELL

        self.offset_x, self.offset_y = GridConfig.offset()

        self.grid = []            # 2D list of tokens
        self.walls = []           # list of pygame.Rect (permanent)
        self.spawn_cell = None    # (col, row)

        # markers extracted from map
        self.task_cells = {}          # dict: "A"/"B"/... -> list[(c,r)]
        self.task_cells_cycle2 = {}   # dict: "a"/"b"/... -> list[(c,r)]
        self.discovery_cells = {}     # dict: "x"/"y"/"z" -> list[(c,r)]
        self.anomaly_cells = {}       # dict: "o"/"p" -> list[(c,r)]

        self.sensor_spawns = []       # list of dicts: {"cell":(c,r), "dir":"U/D/L/R"}
        self.future_wall_cells = []   # list[(c,r)] for "!"
        self.toggle_wall_cells = []   # list[(c,r)] for "?"

        self._load_csv()
        self._index_markers()
        self._build_walls()

        # debug toggle (optional)
        self.debug_draw_markers = True

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
                if token == self.SPAWN:
                    self.spawn_cell = (c, r)

        if self.spawn_cell is None:
            raise ValueError("Map missing spawn cell 'S'")

        self.grid = grid

    def _index_markers(self):
        # reset
        self.task_cells = {}
        self.task_cells_cycle2 = {}
        self.discovery_cells = {}
        self.anomaly_cells = {}

        self.sensor_spawns = []
        self.future_wall_cells = []
        self.toggle_wall_cells = []

        for r in range(self.rows):
            for c in range(self.cols):
                token = self.grid[r][c]

                # tasks
                if token in self.TASKS_CYCLE_1:
                    self.task_cells.setdefault(token, []).append((c, r))
                elif token in self.TASKS_CYCLE_2:
                    self.task_cells_cycle2.setdefault(token, []).append((c, r))

                # discoveries
                elif token in self.DISCOVERIES_CYCLE_2:
                    self.discovery_cells.setdefault(token, []).append((c, r))

                # anomalies
                elif token in self.ANOMALIES_CYCLE_1:
                    self.anomaly_cells.setdefault(token, []).append((c, r))

                # sensors
                elif token in (self.SENSOR_UP, self.SENSOR_DOWN, self.SENSOR_LEFT, self.SENSOR_RIGHT):
                    d = None
                    if token == self.SENSOR_UP:
                        d = "U"
                    elif token == self.SENSOR_DOWN:
                        d = "D"
                    elif token == self.SENSOR_LEFT:
                        d = "L"
                    elif token == self.SENSOR_RIGHT:
                        d = "R"
                    self.sensor_spawns.append({"cell": (c, r), "dir": d})

                # dynamic walls (behaviour later)
                elif token == self.FUTURE_WALL:
                    self.future_wall_cells.append((c, r))
                elif token == self.TOGGLE_WALL:
                    self.toggle_wall_cells.append((c, r))

    def _cell_rect(self, c, r):
        x = self.offset_x + c * self.cell
        y = self.offset_y + r * self.cell
        return pygame.Rect(x, y, self.cell, self.cell)

    def _build_walls(self):
        # only permanent walls for now
        self.walls = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == self.WALL:
                    self.walls.append(self._cell_rect(c, r))

    def get_walls(self):
        return self.walls

    def get_spawn_point(self):
        c, r = self.spawn_cell
        rect = self._cell_rect(c, r)
        # keep existing behaviour: spawn at cell top-left
        return rect.x, rect.y

    # --- helpers you’ll use next (tasks/sensors/discoveries) ---

    def cell_to_world(self, c, r, centre=False):
        rect = self._cell_rect(c, r)
        if centre:
            return rect.centerx, rect.centery
        return rect.x, rect.y

    def get_task_cells(self, cycle=1):
        # returns dict of zones -> list of (c,r)
        if cycle == 2:
            return self.task_cells_cycle2
        return self.task_cells

    def get_discovery_cells(self):
        return self.discovery_cells

    def get_anomaly_cells(self):
        return self.anomaly_cells

    def get_sensor_spawns(self):
        return self.sensor_spawns

    def get_dynamic_wall_cells(self):
        return {
            "future": list(self.future_wall_cells),
            "toggle": list(self.toggle_wall_cells),
        }

    def render(self, screen, phosphor_alpha):
        col = Colour.phosphor_colour(Colour.BRIGHT_GREEN, phosphor_alpha)

        # permanent walls
        for wall in self.walls:
            pygame.draw.rect(screen, col, wall)

        # optional debug overlay
        if not self.debug_draw_markers:
            return

        # spawn marker (small square)
        sx, sy = self.cell_to_world(self.spawn_cell[0], self.spawn_cell[1])
        pygame.draw.rect(screen, Colour.BRIGHT_GREEN, pygame.Rect(sx + 4, sy + 4, 8, 8), 1)

        # sensors (small orange dot)
        for s in self.sensor_spawns:
            cx, cy = self.cell_to_world(s["cell"][0], s["cell"][1], centre=True)
            pygame.draw.circle(screen, Colour.SENSOR, (cx, cy), 3)

        # dynamic walls (outline only)
        for c, r in self.future_wall_cells:
            pygame.draw.rect(screen, Colour.BRIGHT_GREEN, self._cell_rect(c, r), 1)
        for c, r in self.toggle_wall_cells:
            pygame.draw.rect(screen, Colour.BRIGHT_GREEN, self._cell_rect(c, r), 1)

        # task zones (outline)
        for k, cells in self.task_cells.items():
            for c, r in cells:
                cx, cy = self.cell_to_world(c, r, centre=True)
                pygame.draw.circle(screen, Colour.BRIGHT_GREEN, (cx, cy), 2)

        # discoveries (outline)
        for k, cells in self.discovery_cells.items():
            for c, r in cells:
                pygame.draw.rect(screen, Colour.BRIGHT_GREEN, self._cell_rect(c, r), 1)