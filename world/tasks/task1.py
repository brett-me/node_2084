import random
import pygame
from config.palette import Colour


class Task1PathOptimisation:
    """
    Task 1 (Cycle 1):
    - Structured randomness using anchor tokens: a,b,c,d (corners) + e (centre, always last).
      Layout: a=top-left, b=top-right, c=bottom-right, d=bottom-left.
    - Start corner random, direction random (clockwise / anticlockwise).
    - Progressive activation:
        * current target glows
        * when activated, NEXT target appears immediately (or after delay)
        * the just-completed tile keeps glowing until player leaves its activation zone (linger)
        * completed tiles remain visible (locked)
        * future tiles are hidden
    - When all done: wait, then fade all to processed.
    - Activation uses a cell-radius around the ACTIVE tile (fair vs big glow halo).
    """

    STATE_IDLE = "idle"
    STATE_RUNNING = "running"
    STATE_WAITING_NEXT = "waiting_next"
    STATE_COMPLETE_PENDING = "complete_pending"
    STATE_FADING_TO_PROCESSED = "fading_to_processed"
    STATE_PROCESSED = "processed"

    def __init__(self, anchor_cells, *, seed=None):
        """
        anchor_cells: dict like {"a":(c,r), "b":(c,r), "c":(c,r), "d":(c,r), "e":(c,r)}
        """
        self.rng = random.Random(seed)

        self.anchors = dict(anchor_cells)
        required = {"a","b","c","d","e","f","g","h","i","j","k","l","m"}
        missing = required - set(self.anchors.keys())
        if missing:
            raise ValueError(f"Task1 missing anchors: {sorted(missing)}")

        self.cells = self._select_structured_path()

        self.index = 0
        self.completed = set()

        self.state = self.STATE_IDLE

        # timing
        self.complete_pending_timer = 0.0
        self.fade_timer = 0.0
        self.complete_pause_s = 1.0
        self.fade_duration_s = 1.0

        # delay between locking and revealing next target (0 = instant)
        self.next_spawn_delay_s = 0.1
        self.next_spawn_timer = 0.0

        # hit-area fairness: 1 => 3x3 area, 2 => 5x5 area
        self.activation_radius_cells = 1

        # linger: the last-completed cell keeps the ACTIVE glow until player leaves its zone
        self._linger_cell = None

        # step guard
        self._last_player_cell = None

        # glow tuning (your current preference)
        self.active_glow_layers = [
            (18, 10),
            (12, 18),
            (8,  28),
            (4,  45),
        ]

    # ----------------------------
    # Path selection (structured)
    # ----------------------------

    def _select_structured_path(self):
        """
        Perimeter: a b c d e f g h (clockwise)
        Allowed starts: b d f h
        Direction: CW or CCW
        After completing perimeter, spawn bridge based on finishing corner:
            a->i, c->j, e->k, g->l
        Then centre m last.
        """
        cw_ring = ["a", "b", "c", "d", "e", "f", "g", "h"]

        # Safety: ensure we have everything we might reference
        required = set(cw_ring) | {"i", "j", "k", "l", "m"}
        missing = required - set(self.anchors.keys())
        if missing:
            raise ValueError(f"Task1 missing anchors: {sorted(missing)}")

        cw_next = {cw_ring[i]: cw_ring[(i + 1) % len(cw_ring)] for i in range(len(cw_ring))}
        ccw_next = {cw_ring[i]: cw_ring[(i - 1) % len(cw_ring)] for i in range(len(cw_ring))}

        start = self.rng.choice(["b", "d", "f", "h"])
        nxt = cw_next if self.rng.choice([True, False]) else ccw_next

        # Walk the full perimeter (8 unique points)
        order = [start]
        while len(order) < 8:
            order.append(nxt[order[-1]])

        end_corner = order[-1]  # should be one of a/c/e/g
        bridge_for_end = {"a": "i", "c": "j", "e": "k", "g": "l"}

        if end_corner not in bridge_for_end:
            raise ValueError(f"Unexpected perimeter end '{end_corner}'. Check ring/start rules.")

        order.append(bridge_for_end[end_corner])
        order.append("m")

        return [self.anchors[t] for t in order]

    # ----------------------------
    # State / helpers
    # ----------------------------

    @property
    def started(self):
        return self.state != self.STATE_IDLE

    @property
    def is_complete(self):
        return self.state in (
            self.STATE_COMPLETE_PENDING,
            self.STATE_FADING_TO_PROCESSED,
            self.STATE_PROCESSED,
        )

    def start(self, player_cell=None):
        if self.state == self.STATE_IDLE:
            self.state = self.STATE_RUNNING
        self._last_player_cell = player_cell

    def _current_target(self):
        if self.index >= len(self.cells):
            return None
        return self.cells[self.index]

    def _player_in_zone(self, player_cell, centre_cell):
        if player_cell is None or centre_cell is None:
            return False
        pc, pr = player_cell
        tc, tr = centre_cell
        r = self.activation_radius_cells
        return abs(pc - tc) <= r and abs(pr - tr) <= r

    def _update_linger(self, player_cell):
        # Linger ends the moment the player leaves the activation zone of the linger cell.
        if self._linger_cell is None:
            return
        if not self._player_in_zone(player_cell, self._linger_cell):
            self._linger_cell = None

    # ----------------------------
    # Update
    # ----------------------------

    def update(self, dt, player_cell):
        if self.state == self.STATE_IDLE:
            self._last_player_cell = player_cell
            return

        # update linger in all active states
        self._update_linger(player_cell)

        if self.state == self.STATE_PROCESSED:
            self._last_player_cell = player_cell
            return

        if self.state == self.STATE_RUNNING:
            target = self._current_target()
            if target is None:
                self.state = self.STATE_COMPLETE_PENDING
                self.complete_pending_timer = 0.0
                self._last_player_cell = player_cell
                return

            stepped_newly = (
                player_cell is not None
                and player_cell != self._last_player_cell
                and self._player_in_zone(player_cell, target)
            )

            if stepped_newly:
                self.completed.add(target)

                # begin linger on the just-completed target
                self._linger_cell = target

                # last tile?
                if self.index >= len(self.cells) - 1:
                    self.index += 1
                    self.state = self.STATE_COMPLETE_PENDING
                    self.complete_pending_timer = 0.0
                else:
                    # reveal next either instantly or after delay
                    if self.next_spawn_delay_s <= 0:
                        self.index += 1
                        self.state = self.STATE_RUNNING
                    else:
                        self.state = self.STATE_WAITING_NEXT
                        self.next_spawn_timer = 0.0

        elif self.state == self.STATE_WAITING_NEXT:
            self.next_spawn_timer += dt
            if self.next_spawn_timer >= self.next_spawn_delay_s:
                self.index += 1
                self.state = self.STATE_RUNNING

        elif self.state == self.STATE_COMPLETE_PENDING:
            self.complete_pending_timer += dt
            if self.complete_pending_timer >= self.complete_pause_s:
                self.state = self.STATE_FADING_TO_PROCESSED
                self.fade_timer = 0.0

        elif self.state == self.STATE_FADING_TO_PROCESSED:
            self.fade_timer += dt
            if self.fade_timer >= self.fade_duration_s:
                self.fade_timer = self.fade_duration_s
                self.state = self.STATE_PROCESSED

        self._last_player_cell = player_cell

    def _fade_t(self):
        if self.state == self.STATE_FADING_TO_PROCESSED:
            if self.fade_duration_s <= 0:
                return 1.0
            return max(0.0, min(1.0, self.fade_timer / self.fade_duration_s))
        if self.state == self.STATE_PROCESSED:
            return 1.0
        return 0.0

    # ----------------------------
    # Rendering
    # ----------------------------

    def _cell_rect(self, game_map, cell):
        rect = pygame.Rect(0, 0, game_map.cell, game_map.cell)
        cx, cy = game_map.cell_center(cell)
        rect.center = (cx, cy)
        return rect

    def _draw_glow(self, overlay, rect, rgb, layers):
        for inflate_px, a in layers:
            r = rect.inflate(inflate_px, inflate_px)
            pygame.draw.rect(overlay, (*rgb, a), r)

    def render(self, screen, game_map, phosphor_alpha=255):
        if self.state == self.STATE_IDLE:
            return

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        col_active = Colour.phosphor_colour(Colour.TASK1_ACTIVE, phosphor_alpha)
        col_locked = Colour.phosphor_colour(Colour.TASK1_LOCKED, phosphor_alpha)
        col_processed = Colour.phosphor_colour(Colour.TASK1_PROCESSED, phosphor_alpha)

        target = self._current_target()
        fade_t = self._fade_t()

        # Visibility:
        # RUNNING/WAITING_NEXT: show completed + current target + linger cell (if any)
        # COMPLETE_PENDING/FADING/PROCESSED: show all
        if self.state in (self.STATE_RUNNING, self.STATE_WAITING_NEXT):
            visible = []
            for cell in self.cells:
                if cell in self.completed or cell == target or cell == self._linger_cell:
                    visible.append(cell)
        else:
            visible = list(self.cells)

        for cell in visible:
            rect = self._cell_rect(game_map, cell)

            if self.state == self.STATE_COMPLETE_PENDING:
                fill_col = col_locked
                fill_alpha = 120

            elif self.state in (self.STATE_FADING_TO_PROCESSED, self.STATE_PROCESSED):
                fill_alpha = int(120 * (1.0 - fade_t) + 50 * fade_t)
                fill_col = col_processed if fade_t >= 1.0 else col_locked

            else:
                # RUNNING / WAITING_NEXT
                # Active glow applies to:
                # - current target
                # - linger cell (just completed, until player leaves its zone)
                is_glowing = (cell == target) or (cell == self._linger_cell)

                if is_glowing:
                    fill_col = col_active
                    fill_alpha = 80
                    self._draw_glow(overlay, rect, col_active, self.active_glow_layers)
                else:
                    fill_col = col_locked
                    fill_alpha = 70

            pygame.draw.rect(overlay, (*fill_col, fill_alpha), rect)

        screen.blit(overlay, (0, 0))