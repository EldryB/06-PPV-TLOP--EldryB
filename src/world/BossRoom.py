from typing import Any, Callable, List, Optional, TypeVar

import pygame

import settings
from src.world.Room import Room
from src.Boss import Boss
from src.Fireball import Fireball


class BossRoom(Room):
    def __init__(self, player: TypeVar("Player"), on_game_over: Callable[[], None], entry_direction: str) -> None:
        self.entry_direction: str            = entry_direction
        self.boss: Optional[Boss]            = None
        self.boss_fireballs: List[Fireball]  = []

        super().__init__(player, on_game_over)

        self._spawn_boss()


    def _generate_entities(self) -> None:
        pass

    def _generate_objects(self) -> None:
        pass

    def _spawn_boss(self) -> None:
        #Coloca al jefe en el lado opuesto a la puerta de entrada
        cx = settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH  * settings.TILE_SIZE // 2
        cy = settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE // 2

        margin = settings.TILE_SIZE * 2   

        if self.entry_direction == "left":        
            bx = settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - margin - 32
            by = cy - 16
        elif self.entry_direction == "right":     
            bx = settings.MAP_RENDER_OFFSET_X + margin
            by = cy - 16
        elif self.entry_direction == "top":       
            bx = cx - 16
            by = settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE - margin - 32
        else:                                     
            bx = cx - 16
            by = settings.MAP_RENDER_OFFSET_Y + margin

        self.boss = Boss(bx, by)
        self.entities.append(self.boss)


    def update(self, dt: float) -> None:
        if self.adjacent_offset_x != 0 or self.adjacent_offset_y != 0:
            return

        self.player.update(dt)

        if self.boss and not self.boss.dead:
            self.boss.process_ai(self, dt)
            self.boss.update(dt)

            # Contacto directo con el jefe son 2 HP de danho
            if self.player.collides(self.boss) and not self.player.invulnerable:
                settings.SOUNDS["hit-player"].play()
                self.player.damage(2)
                self.player.go_invulnerable(1.5)
                if self.player.health <= 0:
                    self.on_game_over()

            if self.boss.health <= 0:
                self.boss.dead = True
                self._open_entry_door()

        for projectile in list(self.projectiles):
            projectile.update(dt)

            if not projectile.dead and self.boss and not self.boss.dead:
                if projectile.collides(self.boss):
                    self.boss.on_arrow_hit()
                    projectile.dead = True
                    if self.boss.health <= 0:
                        self.boss.dead = True
                        self._open_entry_door()

            if projectile.dead:
                self.projectiles.remove(projectile)

        for fireball in list(self.boss_fireballs):
            fireball.update(dt)

            if not fireball.dead and not self.player.invulnerable:
                if fireball.collides(self.player):
                    self.player.health = 0
                    self.on_game_over()
                    return

            if fireball.dead:
                self.boss_fireballs.remove(fireball)


    def render(self, surface: pygame.Surface, camera_offset_x: float = 0, camera_offset_y: float = 0,) -> None:
        super().render(surface, camera_offset_x, camera_offset_y)

        for fireball in self.boss_fireballs:
            fireball.render(surface, camera_offset_x, camera_offset_y)


    def _open_entry_door(self) -> None:
        for doorway in self.doorways:
            if doorway.direction == self.entry_direction:
                doorway.open = True
                settings.SOUNDS["door"].play()
                break
