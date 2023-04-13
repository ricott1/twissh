from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from math import ceil
from .base import Component

class EquipmentSlot(str, Enum):
    HEAD = "head"
    BODY = "body"
    LEGS = "legs"
    SHOES = "shoes"
    BELT = "belt"
    WEAPON = "weapon"

class EquipmentImageOffset(tuple[int, int], Enum):
    HEAD = (3, 1)
    BODY = (2, 13)
    LEGS = (4, 24)
    SHOES = (4, 35)
    BELT = (4, 23)
    WEAPON = (0, 5)
       
@dataclass
class Equipment(Component):
    """
    The equipment held by the entity.
    """
    head: int | None = None
    body: int | None = None
    legs: int | None = None
    shoes: int | None = None
    belt: int | None = None
    weapon: int | None = None
    
    def add(self, slot: EquipmentSlot, entity: int) -> None:
        setattr(self, slot.value, entity)

    def remove(self, slot: EquipmentSlot) -> None:
        setattr(self, slot.value, None)
    
    def get_bonus(self, bonus: str) -> int:
        bonus = 0
        for slot in EquipmentSlot:
            item = getattr(self, slot.value)
            if item is not None:
                bonus += getattr(item, bonus, 0)
        return bonus
    
    