from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

import esper

from .base import Component

class QuickItemSlots(int, Enum):
    NO_SLOTS = 0
    BASE_SLOTS = 2
    MAX_SLOTS = 5
    SMALL_BELT = 1
    MEDIUM_BELT = 2
    LARGE_BELT = 3

@dataclass
class ItemInfo(Component):
    """
    A description of the entity.
    """

    name: str
    description: str

@dataclass
class ConsumableItem(Component):
    effect: Callable[[esper.World, int], None]

@dataclass
class QuickItems(Component):
    slots = {i+1: None for i in range(QuickItemSlots.BASE_SLOTS)}

    @classmethod
    def from_list(cls, items: list[int | None]) -> QuickItems:
        return cls({i: item for i, item in enumerate(items, 1)})
    


@dataclass
class ConsumableItemSlots(Component):
    value: QuickItemSlots
