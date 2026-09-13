
import math
from typing import Any

import pygame

import settings
from src.Entity import Entity
from src.Fireball import Fireball
from src.definitions.entity import ENTITY_DEFS


class Boss(Entity):
    def __init__(self, x: float, y: float) -> None:
        definition = ENTITY_DEFS["boss"]

        super().__init__(
            x=x, y=y,
            width=32, height=32,
            walk_speed=settings.BOSS_WALK_SPEED,
            health=settings.BOSS_HEALTH,
            animation_defs=definition["animations"],
            states={},          
        )

        self.hitpoints = settings.BOSS_HEALTH

        self.immune_to_sword  = True
        self.vulnerable       = False
        self.vulnerable_timer = 0.0

        self.sword_hit_immune       = False
        self.sword_hit_immune_timer = 0.0

        self.arrow_hit_immune       = False
        self.arrow_hit_immune_timer = 0.0

        self.fire_timer = 0.0

        self.change_animation("idle-down")


    def damage(self, amount: int) -> None:
        if self.immune_to_sword or self.sword_hit_immune:
            return
        self.health -= amount
        self.sword_hit_immune       = True
        self.sword_hit_immune_timer = settings.BOSS_SWORD_IMMUNE_AFTER
        settings.SOUNDS["hit-enemy"].play()

    def on_arrow_hit(self) -> None:
        if self.vulnerable or self.arrow_hit_immune:
            return

        self.health -= 1
        self.vulnerable       = True
        self.vulnerable_timer = settings.BOSS_VULNERABLE_DURATION
        self.immune_to_sword  = False
        settings.SOUNDS["hit-enemy"].play()
        self.go_invulnerable(0.2)   # brief hit flash


    def process_ai(self, room: Any, dt: float) -> None:
        player = room.player
        self._update_timers(dt)

        if self.vulnerable:
            self.change_animation(f"idle-{self.direction}")
            return

        self._face_and_move(player, dt)
        self._maybe_fire(player, room, dt)

    def _update_timers(self, dt: float) -> None:
        if self.vulnerable:
            self.vulnerable_timer -= dt
            if self.vulnerable_timer <= 0:
                self.vulnerable       = False
                self.vulnerable_timer = 0.0
                self.immune_to_sword  = True
                
                # After vulnerability ends, become immune to arrows for 5s
                self.arrow_hit_immune       = True
                self.arrow_hit_immune_timer = settings.BOSS_ARROW_IMMUNE_AFTER

        # Arrow immunity
        if self.arrow_hit_immune:
            self.arrow_hit_immune_timer -= dt
            if self.arrow_hit_immune_timer <= 0:
                self.arrow_hit_immune       = False
                self.arrow_hit_immune_timer = 0.0

        # Sword hit cooldown, 1s between hits
        if self.sword_hit_immune:
            self.sword_hit_immune_timer -= dt
            if self.sword_hit_immune_timer <= 0:
                self.sword_hit_immune       = False
                self.sword_hit_immune_timer = 0.0

    def _face_and_move(self, player, dt: float) -> None:
        dx = (player.x + player.width  / 2) - (self.x + self.width  / 2)
        dy = (player.y + player.height / 2) - (self.y + self.height / 2)

        if abs(dx) >= abs(dy):
            self.direction = "right" if dx >= 0 else "left"
        else:
            self.direction = "down" if dy >= 0 else "up"

        dist = math.hypot(dx, dy)
        if dist > settings.BOSS_STOP_DISTANCE:
            speed = self.walk_speed * dt
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
            self.change_animation(f"walk-{self.direction}")
            self._clamp_to_room()
        else:
            self.change_animation(f"idle-{self.direction}")

    def _clamp_to_room(self) -> None:
        min_x = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE
        max_x = settings.MAP_RENDER_OFFSET_X + (settings.MAP_WIDTH  - 1) * settings.TILE_SIZE - self.width
        min_y = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE
        max_y = settings.MAP_RENDER_OFFSET_Y + (settings.MAP_HEIGHT - 1) * settings.TILE_SIZE - self.height
        self.x = max(min_x, min(max_x, self.x))
        self.y = max(min_y, min(max_y, self.y))

    def _maybe_fire(self, player, room: Any, dt: float) -> None:
        self.fire_timer += dt
        if self.fire_timer >= settings.BOSS_FIRE_COOLDOWN:
            self.fire_timer = 0.0
            fireball = Fireball(
                self.x + self.width  / 2,
                self.y + self.height / 2,
                player.x + player.width  / 2,
                player.y + player.height / 2,
            )
            room.boss_fireballs.append(fireball)


    def update(self, dt: float) -> None:
        if self.invulnerable:
            self.flash_timer        += dt
            self.invulnerable_timer += dt
            if self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable          = False
                self.invulnerable_timer    = 0.0
                self.invulnerable_duration = 0.0
                self.flash_timer           = 0.0

        # Active flashing while arrow-immune
        if self.arrow_hit_immune:
            self.flash_timer += dt

        if self.current_animation:
            self.current_animation.update(dt)

    def render(self,surface: pygame.Surface,offset_x: float = 0,offset_y: float = 0,) -> None:
        if self.current_animation:
            frame_idx = self.current_animation.get_current_frame()
            texture_id = getattr(self.current_animation, "texture_id", "boss")
            
            was_invulnerable = self.invulnerable
            if self.arrow_hit_immune:
                self.invulnerable = True

            self.x += offset_x
            self.y += offset_y
            self.render_sprite(surface, texture_id, frame_idx)
            self.x -= offset_x
            self.y -= offset_y

            self.invulnerable = was_invulnerable
