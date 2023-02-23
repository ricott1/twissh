from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import esper

from ..processors.move_actions import (Action, MoveDown, MoveLeft, MoveRight,
                                       MoveUp)
from .base import Component
from .in_location import Direction


@dataclass
class Acting(Component):

    def __post_init__(self) -> None:
        self.action_recoil = 0
        self.movement_recoil = 0
        self.selected_action = None
        self.actions = {
            Direction.UP: MoveUp,
            Direction.DOWN: MoveDown,
            Direction.LEFT: MoveLeft,
            Direction.RIGHT: MoveRight
        }

    def get_action(self, world: esper.World, ent_id: int) -> Action | None:
        return None

class AiAlignment(str, Enum):
    HOSTILE = "hostile"
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"

@dataclass
class Ai(Component):
    alignment: int = 0