from __future__ import annotations
from cmd import PROMPT
from dataclasses import dataclass
from enum import Enum, auto
import os
from typing import Callable
import esper
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

    def __init__(self, world: esper.World, components: list[Component]) -> None:
        self.world = world
        self.id = self.world.create_entity(components)
        for comp in components:
            self.set_component(comp)

    def has_component(self, component: Component) -> bool:
        return hasattr(self, component.__class__.__name__.lower())

    def get_component(self, component: Component) -> Component:
        return getattr(self, component.__class__.__name__.lower())

    def set_component(self, component: Component) -> None:
        self.world.add_component(self.id, component)
        setattr(self, component.__class__.__name__.lower(), component)

    def remove_component(self, component: Component) -> None:
        self.world.remove_component(self.id, component)
        delattr(self, component.__class__.__name__.lower())

    def handle_input(self, _input: str):
        pass


class Actor(Entity):
    """
    Base class for all entities that can be rendered on the screen.
    """

    def __init__(self, _id: int, name: str, description: str, race: RaceType, gender: GenderType) -> None:
        components = [
            Position(0, 0, 0),
            ImageCollection.CHARACTERS[gender][race],
            RenderableWithDirection("red", markers),
            Directionable(),
            Characteristics(),
            Race(race),
            Gender(gender),
            Description(name, description),
        ]
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


class Health(Component):
    def __init__(self, value: int = 10 + roll3d6()) -> None:
        self.value = value
        self.max_value = value


class Mana(Component):
    def __init__(self, value: int = 10 + roll3d6()) -> None:
        self.value = value
        self.max_value = value


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

    def __str__(self) -> str:
        return f"({self.STRENGTH}, {self.DEXTERITY}, {self.CONSTITUTION}, {self.INTELLIGENCE}, {self.WISDOM}, {self.CHARISMA})"


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


class HPPotionImageCollection(object):
    LARGE = Image(pg.image.load(f"{fileDir}/assets/potions/hp_large.png"))
    MEDIUM = Image(pg.image.load(f"{fileDir}/assets/potions/hp_medium.png"))
    SMALL = Image(pg.image.load(f"{fileDir}/assets/potions/hp_small.png"))


class MPPotionImageCollection(object):
    LARGE = Image(pg.image.load(f"{fileDir}/assets/potions/mp_large.png"))
    MEDIUM = Image(pg.image.load(f"{fileDir}/assets/potions/mp_medium.png"))
    SMALL = Image(pg.image.load(f"{fileDir}/assets/potions/mp_small.png"))


class RejuvenationPotionImageCollection(object):
    LARGE = Image(pg.image.load(f"{fileDir}/assets/potions/rejuvenation_large.png"))
    MEDIUM = Image(pg.image.load(f"{fileDir}/assets/potions/rejuvenation_medium.png"))
    SMALL = Image(pg.image.load(f"{fileDir}/assets/potions/rejuvenation_small.png"))


class CurePotionImageCollection(object):
    LARGE = Image(pg.image.load(f"{fileDir}/assets/potions/cure_large.png"))
    MEDIUM = Image(pg.image.load(f"{fileDir}/assets/potions/cure_medium.png"))
    SMALL = Image(pg.image.load(f"{fileDir}/assets/potions/cure_small.png"))


class HPBottleImageCollection(object):
    L0 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp0.png"))
    L1 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp1.png"))
    L2 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp2.png"))
    L3 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp3.png"))
    L4 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp4.png"))
    L5 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp5.png"))
    L6 = Image(pg.image.load(f"{fileDir}/assets/bottles/hp6.png"))


class MPBottleImageCollection(object):
    L0 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp0.png"))
    L1 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp1.png"))
    L2 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp2.png"))
    L3 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp3.png"))
    L4 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp4.png"))
    L5 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp5.png"))
    L6 = Image(pg.image.load(f"{fileDir}/assets/bottles/mp6.png"))


class ImageCollection(object):
    EMPTY = Image(pg.Surface((0, 0), pg.SRCALPHA))
    BACKGROUND_SELECTED = Image(pg.image.load(f"{fileDir}/assets/background_selected.png"))
    BACKGROUND_UNSELECTED = Image(pg.image.load(f"{fileDir}/assets/background_unselected.png"))
    CHARACTERS = {
        GenderType.FEMALE: {
            k: Image(pg.image.load(f"{fileDir}/assets/characters/{k.lower()}_female.png")) for k in RaceType
        },
        GenderType.MALE: {
            k: Image(pg.image.load(f"{fileDir}/assets/characters/{k.lower()}_male.png")) for k in RaceType
        },
    }

    HP_BOTTLE = HPBottleImageCollection()
    MP_BOTTLE = MPBottleImageCollection()
    HP_POTION = HPPotionImageCollection()
    MP_POTION = MPPotionImageCollection()
    REJUVENATION_POTION = RejuvenationPotionImageCollection()
    CURE_POTION = CurePotionImageCollection()


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
