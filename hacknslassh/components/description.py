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

class Size(Enum):
    CAT = auto()
    SHORT = auto()
    MEDIUM = auto()
    TALL = auto()
    LARGE = auto()

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

    @classmethod
    def get_size_from_game_class(cls, game_class: GameClassName) -> Size:
        if game_class == GameClassName.CAT:
            return Size.CAT
        if game_class == GameClassName.ELF:
            return Size.TALL
        if game_class == GameClassName.ORC:
            return Size.LARGE
        if game_class == GameClassName.DWARF:
            return Size.SHORT
        if game_class == GameClassName.HUMAN:
            return Size.MEDIUM
    @property
    def size(self) -> Size:
        return self.get_size_from_game_class(self.game_class)

@dataclass
class ID(Component):  
    uuid: bytes

    
