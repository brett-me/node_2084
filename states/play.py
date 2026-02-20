
import pygame

from world.map import Map
from world.suspicion import Suspicion
from world.player import Player
from ui.message_banner import MessageSystem
from config.settings import TimingConfig
from config.palette import Colour
from config.grid import GridConfig
from utils.paths import asset_path


class PlayState:
    """main gameplay: movement, sensors, tasks, discoveries"""

    def __init__(self, font, starting_suspicion=0):
        self.machine = None
        self.game = None
        self.font = font

        self.timer = 0.0

        self.map = Map(asset_path("maps", "map_2048.csv"))
        self.walls = self.map.get_walls()
        self.player = None

        self.suspicion = Suspicion()
        self.suspicion.value = starting_suspicion
        self.show_suspicion = False

        # for now: focus on permanent walls rendering; sensors come next step
        self.sensors = []
        self.sensor_active = False

        self.has_moved = False

        self.msg_banner = MessageSystem(self.font, "MOVEMENT ACKNOWLEDGED")
        self.msg_shown = False

    def update(self, dt):
        self.timer += dt
        walls = self.walls

        if self.timer >= TimingConfig.PLAYER_SPAWN_DELAY and self.player is None:
            x, y = self.map.get_spawn_point()
            self.player = Player(x, y)

        moved_this_frame = False
        if self.player:
            self.player.fade(dt)

            if self.player.alpha >= 255:
                moved_this_frame = self.player.move(dt, walls)
                self.show_suspicion = True

            if moved_this_frame:
                self.has_moved = True

        if self.timer >= TimingConfig.SENSOR_START_DELAY:
            self.sensor_active = True

        detected = False
        if self.sensor_active and self.player and self.sensors:
            for sensor in self.sensors:
                if sensor.update(dt, self.player, self.suspicion):
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

        if self.sensors:
            for sensor in self.sensors:
                sensor.render(screen, draw_cone=False)

            if self.sensor_active:
                for sensor in self.sensors:
                    sensor.render(screen)

        if self.player:
            self.player.render(screen)

        if self.show_suspicion:
            self.draw_suspicion_meter(screen)

        self.msg_banner.render(screen, Colour.BRIGHT_GREEN)