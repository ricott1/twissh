from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from math import ceil
from .base import Component


class GameClassName(str, Enum):
    ELF = "Elf"
    DWARF = "Dwarf"
    HUMAN = "Human"
    ORC = "Orc"
    BARD = "Bard"
    SLIME = "Slime"
    DEVIL = "Devil"
    DWARVIL = "Dwarvil"
    CAT = "Cat"

class GenderType(Enum):
    FEMALE = 0
    MALE = 1

class Language(str, Enum):
    COMMON = "Common"
    GATTESE = "Gattese"

    @classmethod
    def encrypt(cls, text: str, language: Language) -> str:
        if language == Language.COMMON:
            return text
        if language == Language.GATTESE:
            return "miao " * ceil(len(text)/5)

@dataclass
class ActorInfo(Component):
    """
    A description of the entity.
    """

    name: str
    description: str
    game_class: GameClassName
    gender: GenderType
    languages: list[Language]
    age: int

@dataclass
class ID(Component):  
    uuid: bytes

    
