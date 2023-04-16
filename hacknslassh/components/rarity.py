from __future__ import annotations
from dataclasses import dataclass
from enum import auto, Enum
from .base import Component
from hacknslassh.color_utils import Color


class RarityLevel(Enum):
    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    LEGENDARY = 3
    UNIQUE = 4

@dataclass
class Rarity(Component):
    level: RarityLevel

    @classmethod
    def common(cls) -> Rarity:
        return Rarity(RarityLevel.COMMON)
    
    @classmethod
    def uncommon(cls) -> Rarity:
        return Rarity(RarityLevel.UNCOMMON)
    
    @classmethod
    def rare(cls) -> Rarity:
        return Rarity(RarityLevel.RARE)
    
    @classmethod
    def legendary(cls) -> Rarity:
        return Rarity(RarityLevel.LEGENDARY)
    
    @classmethod
    def unique(cls) -> Rarity:
        return Rarity(RarityLevel.UNIQUE)
    
    def __post_init__(self) -> None:
        if self.level == RarityLevel.COMMON.value:
            self.color = Color.GRAY
        elif self.level == RarityLevel.UNCOMMON.value:
            self.color = Color.CYAN
        elif self.level == RarityLevel.RARE.value:
            self.color = Color.YELLOW
        elif self.level == RarityLevel.LEGENDARY.value:
            self.color = Color.PURPLE
        elif self.level == RarityLevel.UNIQUE.value:
            self.color = Color.KHAKI
        else:
            self.color = Color.WHITE
        