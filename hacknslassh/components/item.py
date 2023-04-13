from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

import esper

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

    @classmethod
    def common(cls):
        return cls(Rarity.COMMON)
    
    @classmethod
    def uncommon(cls):
        return cls(Rarity.UNCOMMON)
    
    @classmethod
    def rare(cls):
        return cls(Rarity.RARE)
    
    @classmethod
    def legendary(cls):
        return cls(Rarity.LEGENDARY)
    
    @classmethod
    def unique(cls):
        return cls(Rarity.UNIQUE)

@dataclass
class ConsumableItem(Component):
    effect: Callable[[esper.World, int], None]

@dataclass
class EquippableItem(Component):
    requisites: Callable[[esper.World, int], None] | None = None

class QuickItemSlots(int, Enum):
    NO_SLOTS = 0
    BASE_SLOTS = 2
    MAX_SLOTS = 5
    SMALL_BELT = 1
    MEDIUM_BELT = 2
    LARGE_BELT = 3


@dataclass
class ConsumableItemSlots(Component):
    value: QuickItemSlots
