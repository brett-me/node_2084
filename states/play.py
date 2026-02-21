import pygame

from world.map.map import Map
from world.suspicion import Suspicion
from world.player import Player
from ui.message_banner import MessageSystem
from config.settings import TimingConfig
from config.palette import Colour
from config.grid import GridConfig


class PlayState:
    """main gameplay: movement, sensors, tasks, discoveries"""

    def __init__(self, font, starting_suspicion=0):
        self.machine = None
        self.game = None
        self.font = font

        self.timer = 0.0

        self.map = Map("map_2048.csv")
        self.walls = self.map.get_walls()
        self.player = None

        # cycle control
        self.cycle_index = 1

        # permanent / one-way flags
        self.corridor_sealed = False  # T -> activates "!" permanently (never resets)

        # cycle-only door flags (U/V/W -> activate @/%/* for remainder of current cycle)
        self.door12_closed = False
        self.door23_closed = False
        self.room4_trapped = False

        # door group defaults
        self.map.set_group_active("!", False)  # corridor seal (permanent once triggered)
        self.map.set_group_active("@", False)  # room 1->2 one-way close (cycle-only)
        self.map.set_group_active("%", False)  # room 2->3 one-way close (cycle-only)
        self.map.set_group_active("*", False)  # room 4 trap (cycle-only)
        # "$" default is handled inside Map (__init__)

        # marker-driven trigger wiring:
        # trigger token -> (flag_attr_name, wall_group_token, permanent?)
        self.trigger_rules = {
            "T": ("corridor_sealed", "!", True),
            "U": ("door12_closed", "@", False),
            "V": ("door23_closed", "%", False),
            "W": ("room4_trapped", "*", False),
        }

        self.suspicion = Suspicion()
        self.suspicion.value = starting_suspicion
        self.show_suspicion = False

        # --- sensors ---
        # emitters always drawn; cones are staggered by each sensor's own "enabled" latch
        self.sensors = self.map.create_sensors() or []

        self.has_moved = False
        self.msg_banner = MessageSystem(self.font, "MOVEMENT ACKNOWLEDGED")
        self.msg_shown = False

    # -----------------------------
    # Cycle scaffolding (not called yet)
    # -----------------------------
    def _reset_cycle_doors(self):
        """Re-open cycle-only doors at the start of a new cycle."""
        self.door12_closed = False
        self.door23_closed = False
        self.room4_trapped = False

        self.map.set_group_active("@", False)
        self.map.set_group_active("%", False)
        self.map.set_group_active("*", False)

        # IMPORTANT: do NOT touch corridor seal "!" (permanent once triggered)
        # IMPORTANT: do NOT touch return wall "$" here (task-driven later)

        self.walls = self.map.get_walls()

    def advance_cycle(self):
        """Called later when Task 4 completes."""
        self.cycle_index += 1
        self._reset_cycle_doors()

    # -----------------------------
    # Trigger processing
    # -----------------------------
    def _process_triggers(self):
        """Checks player cell against trigger tokens and activates wall groups as needed."""
        if not self.player:
            return

        cell = self.map.world_to_cell(self.player.rect.centerx, self.player.rect.centery)
        if cell is None:
            return

        changed = False

        for trigger_token, (flag_name, wall_token, _is_permanent) in self.trigger_rules.items():
            if getattr(self, flag_name):
                continue

            if self.map.is_trigger(cell, trigger_token):
                setattr(self, flag_name, True)
                self.map.set_group_active(wall_token, True)
                changed = True

        if changed:
            self.walls = self.map.get_walls()

    # -----------------------------
    # Update / Render
    # -----------------------------
    def update(self, dt):
        self.timer += dt

        # spawn player after delay (unchanged behaviour)
        if self.timer >= TimingConfig.PLAYER_SPAWN_DELAY and self.player is None:
            x, y = self.map.get_spawn_point()
            self.player = Player(x, y)

        # movement / collision
        moved_this_frame = False
        if self.player:
            self.player.fade(dt)

            if self.player.alpha >= 255:
                moved_this_frame = self.player.move(dt, self.walls)
                self.show_suspicion = True

            if moved_this_frame:
                self.has_moved = True

        # trigger-driven doors
        self._process_triggers()

        # sensors (no global delay; each sensor enables itself when player first enters its LOS)
        detected = False
        if self.player and self.sensors:
            for sensor in self.sensors:
                if sensor.update(dt, self.map, self.player, self.suspicion):
                    detected = True

        if detected and self.has_moved and not self.msg_shown:
            self.msg_shown = True
            self.msg_banner.trigger(TimingConfig.MSG_DELAY, TimingConfig.MSG_DURATION)

        self.msg_banner.update(dt)

    def draw_grid(self, screen):
        spacing = GridConfig.CELL

        ox, oy = self.map.offset_x, self.map.offset_y
        grid_w = GridConfig.COLS * spacing
        grid_h = GridConfig.ROWS * spacing

        for i in range(GridConfig.COLS + 1):
            x = ox + i * spacing
            pygame.draw.line(screen, Colour.DIM_GREEN, (x, oy), (x, oy + grid_h))

        for j in range(GridConfig.ROWS + 1):
            y = oy + j * spacing
            pygame.draw.line(screen, Colour.DIM_GREEN, (ox, y), (ox + grid_w, y))

    def draw_suspicion_meter(self, screen):
        value = int(self.suspicion.value)
        text = f"SUSPICION: {value}%"

        surf = self.font.render(text, True, Colour.BRIGHT_GREEN)
        padding = 16
        x = screen.get_width() - surf.get_width() - padding
        y = padding

        screen.blit(surf, (x, y))

    def render(self, screen):
        screen.fill(Colour.BACKGROUND)
        self.draw_grid(screen)

        alpha = int(self.game.phosphor.alpha) if self.game else 255
        self.map.render(screen, alpha)

        # sensors: emitters always visible; cones only once each sensor is enabled
        if self.sensors:
            for sensor in self.sensors:
                sensor.render(screen, self.map, draw_cone=False)

            for sensor in self.sensors:
                sensor.render(screen, self.map, draw_cone=True)

        if self.player:
            self.player.render(screen)

        if self.show_suspicion:
            self.draw_suspicion_meter(screen)

        self.msg_banner.render(screen, Colour.BRIGHT_GREEN)