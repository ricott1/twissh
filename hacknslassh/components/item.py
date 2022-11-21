from dataclasses import dataclass
from enum import Enum, auto

from .base import Component


class Rarity(Enum):
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    LEGENDARY = auto()
    UNIQUE = auto()


@dataclass
class ItemRarity(Component):
    """
    Component for item rarity.
    """

    value: Rarity


@dataclass
class Item(Component):
    pass


class QuickItemSlots(int, Enum):
    NO_SLOTS = 0
    BASE_SLOTS = 2
    MAX_SLOTS = 5
    SMALL_BELT = 1
    MEDIUM_BELT = 2
    LARGE_BELT = 3


@dataclass
class Belt(Component):
    slots: QuickItemSlots
