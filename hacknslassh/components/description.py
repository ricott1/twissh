from dataclasses import dataclass
from enum import Enum, auto

from .base import Component


class GameClassName(str, Enum):
    ELF = "Elf"
    DWARF = "Dwarf"
    NERD = "Nerd"
    ORC = "Orc"
    BARD = "Bard"
    SLIME = "Slime"
    DEVIL = "Devil"
    DWARVIL = "Dwarvil"
    CAT = "Cat"

class GenderType(Enum):
    FEMALE = auto()
    MALE = auto()


@dataclass
class Description(Component):
    """
    A description of the entity.
    """

    name: str
    text: str
    game_class: GameClassName
    gender: GenderType
