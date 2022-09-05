from __future__ import annotations
from cmd import PROMPT
from dataclasses import dataclass
from enum import Enum, auto
import os
from typing import Callable
import uuid
from hacknslassh.utils import roll3d6

import pygame as pg


class Component(object):
    """
    Base class for all components.
    """

    pass


class Entity(object):
    """Base Entity class.
    All entities in the game should inherit from this class.
    """
    def __init__(self, components: list[Component]) -> None:
        self.id = uuid.uuid4()
        self._components = {}
        for comp in components:
            self.set_component(comp)

    def has_component(self, component: Component) -> bool:
        return hasattr(self, component.__class__.__name__.lower())
    
    def get_component(self, component: Component) -> Component:
        return getattr(self, component.__class__.__name__.lower())

    def set_component(self, component: Component) -> None:
        setattr(self, component.__class__.__name__.lower(), component)

    def remove_component(self, component: Component) -> None:
        delattr(self, component.__class__.__name__.lower())
        component.remove_entity_attributes(self)

class Actor(Entity):
    """
    Base class for all entities that can be rendered on the screen.
    """
    def __init__(self, _id: uuid.UUID, name: str, description: str, race: RaceType, gender: GenderType) -> None:
        components = [Position(0, 0, 0), ImageCollection.CHARACTERS[gender][race], RenderableWithDirection("red", markers), Directionable(), Characteristics(), Race(race), Gender(gender), Description(name, description)]
        super().__init__(components)
        self.id = _id

        self.counters = {}
        self.location = None

@dataclass
class Description(Component):
    """
    A description of the entity.
    """
    name: str
    text: str



@dataclass
class Position(Component, pg.math.Vector3):
    """
    Component for position.
    """
    def __init__(self, vector3: pg.math.Vector3 = pg.math.Vector3(0, 0, 0), *args) -> None:
        self._vector3 = vector3
        super().__init__(*args)

    def __getattr__(self, attr):
        return self._vector3.__getattribute__(attr)

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

@dataclass
class Velocity(Component, pg.math.Vector3):
    """
    Component for Velocity.
    """

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class Directionable(Component):
    """
    Component for direction.
    """

    direction: Direction = Direction.UP

    def __str__(self) -> str:
        return f"({self.direction})"

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

    def __str__(self) -> str:
        return f"({self.value})"


class CharacteristicType(str, Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"
    HP = "hit-points"
    MP = "mana-points"

@dataclass
class Characteristics(Component):
    """
    Component for characteristics.
    """

    STRENGTH: int = roll3d6()
    DEXTERITY: int = roll3d6()
    CONSTITUTION: int = roll3d6()
    INTELLIGENCE: int = roll3d6()
    WISDOM: int = roll3d6()
    CHARISMA: int = roll3d6()
    HP: int = 10 + roll3d6()
    MP: int = 10 + roll3d6()

    def __str__(self) -> str:
        return f"({self.STRENGTH}, {self.DEXTERITY}, {self.CONSTITUTION}, {self.INTELLIGENCE}, {self.WISDOM}, {self.CHARISMA}, {self.HP}, {self.MP})"

class RaceType(str, Enum):
    ELF = "Elf"
    DWARF = "Dwarf"
    NERD = "Nerd"
    ORC = "Orc"
    BARD = "Bard"
    SLIME = "Slime"
    DEVIL = "Devil"

class GenderType(Enum):
    FEMALE = auto()
    MALE = auto()

@dataclass
class Gender(Component):
    """
    Component for Gender
    """

    value: GenderType

@dataclass
class Race(Component):
    """
    Component for race.
    """

    value: RaceType


class Orc(Entity):
    def __init__(self) -> None:
        super().__init__([Race(RaceType.ORC), Characteristics])

@dataclass
class Image(Component):
    surface: pg.Surface

@dataclass
class Renderable(Component):
    """
    Component for rendering an entity on map.
    """

    marker: str
    color: str

    def __str__(self) -> str:
        return f"({self.char}, {self.color})"

@dataclass
class RenderableWithDirection(Component):
    """
    Component for rendering an entity on map with direction.
    """

    color: str
    # markers: dict[Direction, str]
    markers = {
        Direction.UP: "▲",
        Direction.DOWN: "▼",
        Direction.LEFT: "◀",
        Direction.RIGHT: "▶",
    }

@dataclass
class DelayCallback(Component):
    """
    Component for delaying a callback.
    """

    callback: Callable
    delay: float

    def __str__(self) -> str:
        return f"({self.callback}, {self.delay})"

fileDir = os.path.dirname(os.path.realpath(__file__))

class ImageCollection(object):
    EMPTY = Image(pg.Surface((0, 0), pg.SRCALPHA))
    BACKGROUND_SELECTED = Image(pg.image.load(f"{fileDir}/assets/background_selected.png"))
    BACKGROUND_UNSELECTED = Image(pg.image.load(f"{fileDir}/assets/background_unselected.png"))
    CHARACTERS = {
        GenderType.FEMALE: {
            k: Image(pg.image.load(f"{fileDir}/assets/characters/{k.lower()}_female.png"))
            for k in RaceType
        },
        GenderType.MALE: {
            k: Image(pg.image.load(f"{fileDir}/assets/characters/{k.lower()}_male.png"))
            for k in RaceType
        },
    }
    HP_BOTTLE_0 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp0.png"))
    HP_BOTTLE_1 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp1.png"))
    HP_BOTTLE_2 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp2.png"))
    HP_BOTTLE_3 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp3.png"))
    HP_BOTTLE_4 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp4.png"))
    HP_BOTTLE_5 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp5.png"))
    HP_BOTTLE_6 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp6.png"))
    MP_BOTTLE_0 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp0.png"))
    MP_BOTTLE_1 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp1.png"))
    MP_BOTTLE_2 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp2.png"))
    MP_BOTTLE_3 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp3.png"))
    MP_BOTTLE_4 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp4.png"))
    MP_BOTTLE_5 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp5.png"))
    MP_BOTTLE_6 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp6.png"))

    HP_POTION = Image(pg.image.load(f"{fileDir}/assets/hp_potion.png"))
    MP_POTION = Image(pg.image.load(f"{fileDir}/assets/mp_potion.png"))
   

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