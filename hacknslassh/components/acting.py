from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from hacknslassh.processors.action import Action

from .base import Component

@dataclass
class Acting(Component):
    action_recoil: float = 0
    movement_recoil: float = 0
    selected_action: Action = None
    actions = {}
    target: int | None = None
    auto_target: bool = True

    @classmethod
    def default(cls) -> Acting:
        from hacknslassh.constants import KeyMap
        from hacknslassh.processors.item_action import Drop1, Drop2, Drop3, Drop4, Drop5, PickUp, Use1, Use2, Use3, Use4, Use5
        from hacknslassh.processors.target_action import TargetNext, TargetPrevious, TargetSelf, ToggleAutoTarget
        from hacknslassh.processors.move_actions import MoveDown, MoveLeft, MoveRight, MoveUp
        from hacknslassh.processors.attack_action import Attack
        from hacknslassh.processors.parry_action import Parry
        _acting = Acting()
        _acting.actions = {
            KeyMap.UP: MoveUp,
            KeyMap.DOWN: MoveDown,
            KeyMap.LEFT: MoveLeft,
            KeyMap.RIGHT: MoveRight,
            KeyMap.ATTACK: Attack,
            KeyMap.PARRY: Parry,
            KeyMap.PICK_UP: PickUp,
            KeyMap.DROP_1: Drop1,
            KeyMap.DROP_2: Drop2,
            KeyMap.DROP_3: Drop3,
            KeyMap.DROP_4: Drop4,
            KeyMap.DROP_5: Drop5,
            KeyMap.USE_1: Use1,
            KeyMap.USE_2: Use2,
            KeyMap.USE_3: Use3,
            KeyMap.USE_4: Use4,
            KeyMap.USE_5: Use5,
            KeyMap.TARGET_NEXT: TargetNext,
            KeyMap.TARGET_PREVIOUS: TargetPrevious,
            KeyMap.TARGET_SELF: TargetSelf,
            KeyMap.TOGGLE_AUTO_TARGET: ToggleAutoTarget
        }
        return _acting

class AiAlignment(str, Enum):
    HOSTILE = "hostile"
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"

@dataclass
class Ai(Component):
    alignment: int = 0