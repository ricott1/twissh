from __future__ import annotations
from dataclasses import dataclass

from hacknslassh.processors.transform_actions import TransformToDevil
from .base import Component
from .in_location import Direction
from ..processors.move_actions import MoveDown, MoveUp, MoveLeft, MoveRight, Action

@dataclass
class Acting(Component):
    action_recoil: float = 0
    movement_recoil: float = 0
    selected_action: Action | None = None
    actions = {
        Direction.UP: MoveUp,
        Direction.DOWN: MoveDown,
        Direction.LEFT: MoveLeft,
        Direction.RIGHT: MoveRight,
        "t": TransformToDevil
    }