from src.Projectile import Projectile
import pygame
import settings


class DummyHitbox:

    def __init__(self, x: float, y: float, direction: str) -> None:
        self.x = x
        self.y = y
        self.direction = direction

        if direction in ("up", "down"):
            self.width = settings.ARROW_H
            self.height = settings.ARROW_W
        else:
            self.width = settings.ARROW_W
            self.height = settings.ARROW_H

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def render(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        base_rect = settings.frame("arrow", 1)
        img = pygame.Surface((base_rect.width, base_rect.height), pygame.SRCALPHA)
        img.blit(settings.TEXTURES["arrow"], (0, 0), base_rect)

        if self.direction == "right":
            final = pygame.transform.flip(img, False, False)   
        elif self.direction == "left":
            final = pygame.transform.flip(img, True, False)    
        elif self.direction == "up":
            final = pygame.transform.rotate(img, 90)          
        else:  # down
            final = pygame.transform.rotate(img, -90)         

        surface.blit(final, (self.x + offset_x, self.y + offset_y))


class ArrowFactory:
    @staticmethod
    def create_arrow(player) -> Projectile:
        direction = player.direction

        if direction == "right":
            x = player.x + player.width
            y = player.y + player.height / 2 - settings.ARROW_H / 2
        elif direction == "left":
            x = player.x - settings.ARROW_W
            y = player.y + player.height / 2 - settings.ARROW_H / 2
        elif direction == "up":
            x = player.x + player.width / 2 - settings.ARROW_H / 2
            y = player.y - settings.ARROW_W
        else:  # down
            x = player.x + player.width / 2 - settings.ARROW_H / 2
            y = player.y + player.height

        obj = DummyHitbox(x, y, direction)
        return Projectile(obj, direction)


class Bow:
    def __init__(self) -> None:
        self.factory = ArrowFactory()
        self._cooldown_timer: float = 0.0  

    def tick(self, dt: float) -> None:
        if self._cooldown_timer > 0:
            self._cooldown_timer = max(0.0, self._cooldown_timer - dt)

    def fire(self, player) -> "Projectile | None":
        if self._cooldown_timer > 0:
            return None
        self._cooldown_timer = settings.BOW_COOLDOWN
        return self.factory.create_arrow(player)