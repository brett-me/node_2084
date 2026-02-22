import pygame
from config.palette import Colour
from config.grid import GridConfig
from utils.paths import asset_path


class Map:
    """Loads tile map from CSV. Owns static walls, dynamic wall groups, triggers, and marker cells."""

    STATIC_WALL = "#"
    SPAWN = "S"

    # dynamic wall groups (inactive unless toggled)
    DYNAMIC_WALL_TOKENS = {"!", "@", "%", "*", "$"}

    # trigger cells (cause toggles)
    TRIGGER_TOKENS = {"T", "U", "V", "W"}

    # sensor emitter tokens (placed on wall cells)
    SENSOR_TOKENS = {"^", "v", "<", ">"}

    # Task 1 trigger token(s)
    TASK1_TRIGGER_TOKENS = {"1"}

    # Task 1 structured anchors
    TASK1_ANCHOR_TOKENS = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m"}

    def __init__(self, csv_filename):
        self.csv_path = asset_path(csv_filename)

        self.cols = GridConfig.COLS
        self.rows = GridConfig.ROWS
        self.cell = GridConfig.CELL
        self.offset_x, self.offset_y = GridConfig.offset()

        self.grid = []
        self.spawn_cell = None

        # walls
        self.static_walls = []
        self.dynamic_cells = {tok: [] for tok in self.DYNAMIC_WALL_TOKENS}
        self.dynamic_active = {tok: False for tok in self.DYNAMIC_WALL_TOKENS}
        self.dynamic_active["$"] = True  # return wall default ON

        # triggers
        self.triggers = {tok: set() for tok in self.TRIGGER_TOKENS}

        # sensors: list of ((c,r), token)
        self.sensor_emitters = []

        # task markers (new)
        self.task1_triggers = set()   # set[(c,r)]
        self.task1_anchors = {}       # dict[str] -> (c,r)

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

                if token in self.SENSOR_TOKENS:
                    # emitter lives on this wall cell; direction is the token
                    self.sensor_emitters.append(((c, r), token))

                # ---- Task 1 parsing (new) ----
                if token in self.TASK1_TRIGGER_TOKENS:
                    self.task1_triggers.add((c, r))

                if token in self.TASK1_ANCHOR_TOKENS:
                    # enforce uniqueness: if you accidentally place two 'a' tokens,
                    # you'll notice immediately instead of silently picking one.
                    if token in self.task1_anchors:
                        raise ValueError(f"Duplicate Task1 anchor '{token}' at {(c, r)}")
                    self.task1_anchors[token] = (c, r)

            grid.append(row)

        if self.spawn_cell is None:
            raise ValueError("Map missing spawn cell 'S'")

        self.grid = grid

    def _cell_rect(self, c, r):
        x = self.offset_x + c * self.cell
        y = self.offset_y + r * self.cell
        return pygame.Rect(x, y, self.cell, self.cell)

    def _build_static_walls(self):
        """
        Static walls include:
        - '#'
        - sensor emitter cells (^ v < >) so you don't get holes in wall lines
        """
        self.static_walls = []
        for r in range(self.rows):
            for c in range(self.cols):
                t = self.grid[r][c]
                if t == self.STATIC_WALL or t in self.SENSOR_TOKENS:
                    self.static_walls.append(self._cell_rect(c, r))

    def create_sensors(self):
        from world.sensors import Sensor
        sensors = []
        for (cell, direction) in self.sensor_emitters:
            sensors.append(Sensor(cell=cell, direction_token=direction, max_length_cells=30))
        return sensors

    def get_spawn_point(self):
        c, r = self.spawn_cell
        rect = self._cell_rect(c, r)
        return rect.x, rect.y

    def world_to_cell(self, x, y):
        gx = x - self.offset_x
        gy = y - self.offset_y
        if gx < 0 or gy < 0:
            return None
        c = int(gx // self.cell)
        r = int(gy // self.cell)
        if c < 0 or c >= self.cols or r < 0 or r >= self.rows:
            return None
        return (c, r)

    def in_bounds(self, cell):
        if cell is None:
            return False
        c, r = cell
        return 0 <= c < self.cols and 0 <= r < self.rows

    def token_at(self, cell):
        if not self.in_bounds(cell):
            return None
        c, r = cell
        return self.grid[r][c]

    def is_trigger(self, cell, trigger_token):
        if cell is None:
            return False
        return cell in self.triggers.get(trigger_token, set())

    # ---- Task 1 helpers (new) ----

    def is_task1_trigger(self, cell):
        """True if player is standing on a Task 1 trigger cell (token '1')."""
        if cell is None:
            return False
        return cell in self.task1_triggers

    def get_task1_anchors(self):
        required = self.TASK1_ANCHOR_TOKENS
        missing = required - set(self.task1_anchors.keys())
        if missing:
            raise ValueError(f"Task1 anchors missing on map: {sorted(missing)}")
        return dict(self.task1_anchors)

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

    def is_wall_cell(self, cell):
        t = self.token_at(cell)
        if t is None:
            return False
        if t == self.STATIC_WALL:
            return True
        if t in self.SENSOR_TOKENS:
            return True
        if t in self.DYNAMIC_WALL_TOKENS:
            return bool(self.dynamic_active.get(t, False))
        return False

    def is_sensor_occluder(self, cell, behaviour="A"):
        t = self.token_at(cell)
        if t is None:
            return True
        if t == self.STATIC_WALL:
            return True
        if t in self.SENSOR_TOKENS:
            return True
        if t in self.DYNAMIC_WALL_TOKENS:
            if behaviour == "B":
                return True
            return bool(self.dynamic_active.get(t, False))
        return False

    def cell_center(self, cell):
        c, r = cell
        x = self.offset_x + c * self.cell + self.cell // 2
        y = self.offset_y + r * self.cell + self.cell // 2
        return x, y

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