import pygame
from world.map import Map
from world.suspicion import Suspicion
from world.sensors import Sensor
from world.player import Player
from ui.message_banner import MessageSystem
from config.settings import TimingConfig
from config.palette import Colour


class PlayState:
    """main gameplay: movement, sensors, tasks, discoveries"""

    def __init__(self, font, starting_suspicion=0):
        self.machine = None

        self.timer = 0
        self.player = None

        self.map = Map(offset_y=100)

        self.suspicion = Suspicion()
        self.suspicion.value = starting_suspicion

        self.show_suspicion = False
        self.font = font

        self.sensor = Sensor(origin=(114, 360), length=584, spread=72)
        self.sensor_active = False

        self.has_moved = False

        self.msg_banner = MessageSystem(self.font, "MOVEMENT ACKNOWLEDGED")
        self.msg_shown = False

    def update(self, dt):
        self.timer += dt
        walls = self.map.get_walls()

        if self.timer >= TimingConfig.PLAYER_SPAWN_DELAY:
            if self.player is None:
                x, y = self.map.get_spawn_points
                self.player = Player(x, y)

        if self.player:
            self.player.fade(dt)

            moved_this_frame = False

            if self.player.alpha >= 255:
                moved_this_frame = self.player.move(dt, walls)

            if moved_this_frame:
                self.has_moved = True

            if self.player.alpha >= 255:
                self.show_suspicion = True

        if self.timer >= TimingConfig.SENSOR_START_DELAY:
            self.sensor_active = True

        detected = False
        if self.sensor_active:
            detected = self.sensor.update(dt, self.player, self.suspicion)

        if detected and self.has_moved and not self.msg_shown:
            self.msg_shown = True
            self.msg_banner.trigger(TimingConfig.MSG_DELAY, TimingConfig.MSG_DURATION)

        self.msg_banner.update(dt)

    def draw_grid(self, screen):
        spacing = 40
        width, height = screen.get_size()

        for x in range(0, width, spacing):
            pygame.draw.line(screen, Colour.DIM_GREEN, start_pos=(x, 0), end_pos=(x, height))

        for y in range(0, height, spacing):
            pygame.draw.line(screen, Colour.DIM_GREEN, start_pos=(0, y), end_pos=(width, y))

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

        alpha = int(self.machine.game.phosphor.alpha)
        self.map.render(screen, alpha)

        self.sensor.render(screen, draw_cone=False)
        if self.sensor_active:
            self.sensor.render(screen)

        if self.player:
            self.player.render(screen)

        if self.show_suspicion:
            self.draw_suspicion_meter(screen)

        self.msg_banner.render(screen, Colour.BRIGHT_GREEN)
