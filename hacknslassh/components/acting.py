from __future__ import annotations

from dataclasses import dataclass

from ..processors.move_actions import (Action, MoveDown, MoveLeft, MoveRight,
                                       MoveUp)
from .base import Component
from .in_location import Direction


@dataclass
class Acting(Component):
    action_recoil: float = 0
    movement_recoil: float = 0
    selected_action: Action | None = None
    actions = {
        Direction.UP: MoveUp,
        Direction.DOWN: MoveDown,
        Direction.LEFT: MoveLeft,
        Direction.RIGHT: MoveRight
    }
