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
    FEMALE = auto()
    MALE = auto()

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
class Info(Component):
    """
    A description of the entity.
    """

    name: str
    description: str
    game_class: GameClassName
    gender: GenderType
    languages: list[Language]

    @classmethod
    def merge_info(cls, old: Info, new: Info) -> Info:
        _name = new.name if hasattr(new, "name") else old.name
        _description = new.description if hasattr(new, "description") else old.description
        _game_class = new.game_class if hasattr(new, "game_class") else old.game_class
        _gender = new.gender if hasattr(new, "gender") else old.gender
        _languages = new.languages if hasattr(new, "languages") else old.languages
        return Info(_name, _description, _game_class, _gender, _languages)

@dataclass
class CatInfo(Info):
    description = "A serious cat."
    game_class = GameClassName.CAT.value
    languages = [Language.GATTESE, Language.COMMON]

@dataclass
class DevilInfo(Info):
    description = "A serious devil."
    game_class = GameClassName.DEVIL.value

@dataclass
class DwarvilInfo(Info):
    description = "A serious, small devil."
    game_class = GameClassName.DWARVIL.value

    
