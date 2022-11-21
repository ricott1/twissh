from __future__ import annotations
from dataclasses import dataclass
from ..utils import roll3d6

from .base import Component


class Health(Component):
    def __init__(self, value: int = 10 + roll3d6()) -> None:
        self.value = value
        self.max_value = value


@dataclass
class HealthRegeneration(Component):
    """
    Component for health regeneration.
    """

    value: int = 1
    frames_to_regenerate: int = 10
    frame: int = 0


class Mana(Component):
    def __init__(self, value: int = 10 + roll3d6()) -> None:
        self.value = value
        self.max_value = value


@dataclass
class ManaRegeneration(Component):
    """
    Component for mana regeneration.
    """

    value: int = 1
    frames_to_regenerate: int = 10
    frame: int = 0


@dataclass
class Characteristics(Component):
    """
    Component for characteristics.
    """

    STRENGTH: int
    DEXTERITY: int
    CONSTITUTION: int
    INTELLIGENCE: int
    WISDOM: int
    CHARISMA: int

    @classmethod
    def get_random(cls) -> Characteristics:
        return cls(
            STRENGTH=roll3d6(),
            DEXTERITY=roll3d6(),
            CONSTITUTION=roll3d6(),
            INTELLIGENCE=roll3d6(),
            WISDOM=roll3d6(),
            CHARISMA=roll3d6(),
        )
