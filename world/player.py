import pygame
from config.settings import TimingConfig
from config.palette import Colour


class Player:
    """the node: glowing square, grid movement, collision"""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

        self.speed = 160  # pixels per second
        self.alpha = 0  # start invisible

    def fade(self, dt):
        fade_speed = 255 / TimingConfig.PLAYER_FADE_DURATION
        self.alpha += fade_speed * dt

        if self.alpha > 255:
            self.alpha = 255

    def move(self, dt, walls):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_a]:
            dx = -self.speed * dt
        if keys[pygame.K_d]:
            dx = self.speed * dt
        if keys[pygame.K_w]:
            dy = -self.speed * dt
        if keys[pygame.K_s]:
            dy = self.speed * dt

        moved_this_frame = (dx != 0) or (dy != 0)

        self.rect.x += dx
        self.collide(walls, dx, 0)

        self.rect.y += dy
        self.collide(walls, 0, dy)

        return moved_this_frame

    def collide(self, walls, dx, dy):
        """prevents player passing through walls"""

        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                if dx < 0:
                    self.rect.left = wall.right
                if dy > 0:
                    self.rect.bottom = wall.top
                if dy < 0:
                    self.rect.top = wall.bottom

    def render(self, screen):
        surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        surf.fill((*Colour.PLAYER_CORE, int(self.alpha)))
        screen.blit(surf, self.rect.topleft)
