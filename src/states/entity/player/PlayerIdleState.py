
from typing import TypeVar
import pygame
from gale.state import StateMachine
import settings
from src.states.entity.BaseEntityState import BaseEntityState


class PlayerIdleState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon

    def enter(self) -> None:
        self.entity.offset_y = 5
        self.entity.offset_x = 0
        self.entity.change_animation(f"idle-{self.entity.direction}")

    def update(self, dt: float) -> None:
        if self.entity.bow_requested:
            self.entity.bow_requested = False
            if getattr(self.entity, 'has_bow', False) and self.entity.bow is not None:
                arrow = self.entity.bow.fire(self.entity)
                if arrow is not None:
                    self.dungeon.current_room.projectiles.append(arrow)
                    settings.SOUNDS["sword"].play()

        if getattr(self.entity, 'bow', None) is not None:
            self.entity.bow.tick(dt)

        if self.entity.sword_requested:
            self.entity.sword_requested = False
            self.entity.change_state("swing-sword")
            return

        if self.entity.interact_requested:
            self.entity.interact_requested = False
            
            opened_chest = self.dungeon.current_room.open_adjacent_chest(self.entity)
            
            if not opened_chest:
                self.dungeon.current_room.take_adjacent_pot(self.entity)

            if self.entity.state_machine.current is not self:
                return

        held = self.entity.held

        if held["move_left"] or held["move_right"] or held["move_up"] or held["move_down"]:
            self.entity.change_state("walk")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())