
import math

import pygame

import settings


class Fireball:
    def __init__(self, origin_x: float, origin_y: float, target_x: float, target_y: float) -> None:
        r = settings.FIREBALL_RADIUS
        self.width  = r * 2
        self.height = r * 2

        self.x = origin_x - r
        self.y = origin_y - r

        dx = target_x - origin_x
        dy = target_y - origin_y
        dist = math.hypot(dx, dy) or 1.0
        self.vx = dx / dist * settings.FIREBALL_SPEED
        self.vy = dy / dist * settings.FIREBALL_SPEED

        self.dead = False


    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def collides(self, target) -> bool:
        return self.get_collision_rect().colliderect(
            pygame.Rect(round(target.x), round(target.y), target.width, target.height)
        )

    def update(self, dt: float) -> None:
        if self.dead:
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        map_left   = settings.MAP_RENDER_OFFSET_X
        map_right  = settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH  * settings.TILE_SIZE
        map_top    = settings.MAP_RENDER_OFFSET_Y
        map_bottom = settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE

        if (self.x + self.width  < map_left  or self.x > map_right or
                self.y + self.height < map_top or self.y > map_bottom):
            self.dead = True

    def render(
        self,
        surface: pygame.Surface,
        offset_x: float = 0,
        offset_y: float = 0,
    ) -> None:
        r  = settings.FIREBALL_RADIUS
        cx = int(self.x + r + offset_x)
        cy = int(self.y + r + offset_y)
        pygame.draw.circle(surface, (255,  80,  0), (cx, cy), r)
        pygame.draw.circle(surface, (255, 220,  0), (cx, cy), max(1, r - 2))

