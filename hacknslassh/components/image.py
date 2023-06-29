from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Sequence, Union, TypedDict

import pygame as pg
from hacknslassh.color_utils import Color


from .base import Component
from .description import ActorInfo, GenderType, GameClassName, Size

_ColorInput = Union[pg.Color, str, list[int], tuple[int, int, int], tuple[int, int, int, int]]
_RgbaOutput = tuple[int, int, int, int]

class ImageLayer(Enum):
    BASE = auto()
    FEET = auto()
    LEGS = auto()
    TAIL = auto()
    BODY = auto()
    BODY_HAIR = auto()
    HEAD = auto()
    LEGS_EQUIPMENT = auto()
    FEET_EQUIPMENT = auto()
    BODY_EQUIPMENT = auto()
    FACIAL_HAIR = auto()
    HAIR = auto()
    BELT_EQUIPMENT = auto()
    HEAD_EQUIPMENT = auto()
    WEAPON = auto()

class ImageComponent(TypedDict):
    offset: tuple[int, int]
    surface: pg.Surface
    color_map: dict[Color, Color]


ImageComponentOffset = {
    GameClassName.CAT: {
        ImageLayer.TAIL: (0, 19),
        ImageLayer.BODY: (3, 28),
        ImageLayer.BODY_EQUIPMENT: (3, 28),
        ImageLayer.HEAD: (7, 19),
        ImageLayer.HEAD_EQUIPMENT: (7, 19),
        ImageLayer.WEAPON: (0, 16),
    },
    GameClassName.DWARF: {
        ImageLayer.FEET: (2, 35),
        ImageLayer.LEGS: (1, 27),
        ImageLayer.LEGS_EQUIPMENT: (1, 27),
        ImageLayer.BODY: (2, 17),
        ImageLayer.BODY_EQUIPMENT: (2, 17),
        ImageLayer.HEAD: (3, 6),
        ImageLayer.HEAD_EQUIPMENT: (3, 6),
        ImageLayer.WEAPON: (0, 16),

    },
    GameClassName.HUMAN: {
        ImageLayer.FEET: (2, 35),
        ImageLayer.LEGS: (1, 24),
        ImageLayer.LEGS_EQUIPMENT: (1, 24),
        ImageLayer.BODY: (2, 13),
        ImageLayer.BODY_EQUIPMENT: (2, 13),
        ImageLayer.HEAD: (3, 2),
        ImageLayer.HEAD_EQUIPMENT: (3, 2),
        ImageLayer.WEAPON: (0, 16),
    },
    GameClassName.ELF: {
        ImageLayer.FEET: (2, 35),
        ImageLayer.LEGS: (1, 23),
        ImageLayer.LEGS_EQUIPMENT: (1, 23),
        ImageLayer.BODY: (2, 11),
        ImageLayer.BODY_EQUIPMENT: (2, 11),
        ImageLayer.HEAD: (3, 0),
        ImageLayer.HEAD_EQUIPMENT: (3, 0),
        ImageLayer.WEAPON: (0, 16),
    },
    GameClassName.ORC: {
        ImageLayer.FEET: (2, 35),
        ImageLayer.LEGS: (1, 23),
        ImageLayer.LEGS_EQUIPMENT: (1, 23),
        ImageLayer.BODY: (1, 11),
        ImageLayer.BODY_EQUIPMENT: (1, 11),
        ImageLayer.HEAD: (3, 0),
        ImageLayer.HEAD_EQUIPMENT: (3, 0),
        ImageLayer.WEAPON: (0, 16),
    },
}

ColorMaps = {
    "skin": { 
        "light_pink": {
            Color.RED: Color.fromhex("EF8D8A"),
            Color.GREEN: Color.fromhex("F9D9D8"),
        },
        "dark_pink": {
            Color.RED: Color.fromhex("F3B28E"),
            Color.GREEN: Color.fromhex("F9D9B4")
        },
        "brown": {
            Color.RED: Color.fromhex("A98965"),
            Color.GREEN: Color.fromhex("D1B18C")
        },
        "light_green": {
            Color.RED: Color.fromhex("5F5F1A"),
            Color.GREEN: Color.fromhex("688626")
        },
        "dark_green": {
            Color.RED: Color.fromhex("275E16"),
            Color.GREEN: Color.fromhex("3A8524")
        },
        "red": {    
            Color.RED: Color.fromhex("E31619"),
            Color.GREEN: Color.fromhex("FF7E7E")
        }
    },
    "hair": {
        "blonde": {
            Color.RED: Color.fromhex("FFD281"),
            Color.GREEN: Color.fromhex("E1E32A"),
            Color.BLUE: Color.fromhex("FEFF83")
        },
        "black": {
            Color.RED: Color.fromhex("000000"),
            Color.GREEN: Color.fromhex("000000"),
            Color.BLUE: Color.fromhex("000000")
        },
        "grey": {
            Color.RED: Color.fromhex("000000"),
            Color.GREEN: Color.fromhex("5f5f5f"),
            Color.BLUE: Color.fromhex("acacac")
        },
        "brown": {
            Color.RED: Color.fromhex("522506"),
            Color.GREEN: Color.fromhex("000000"),
            Color.BLUE: Color.fromhex("905022")
        },
    },
    "eyes": {
        "blue": {
            Color.BLUE: Color.fromhex("3A85D1"),
        },
        "brown": {
            Color.BLUE: Color.fromhex("A9892C"),
        },
        "green": {
            Color.BLUE: Color.fromhex("275E5E"),
        },
        "dark_brown": { 
            Color.BLUE: Color.fromhex("A46321"),
        },
        "black": {  
            Color.BLUE: Color.fromhex("000000"),
        },
    },
    "fur": {
        "orange": {
            Color.RED: Color.fromhex("FD8B4E"),
            Color.GREEN: Color.fromhex("612400"),
            Color.BLUE: Color.fromhex("FFE0CE"),
            Color.YELLOW: Color.fromhex("FFB48F")
        },
        "grey": {
            Color.RED: Color.fromhex("222222"),
            Color.GREEN: Color.fromhex("161213"),
            Color.BLUE: Color.fromhex("5C5C5C"),
            Color.YELLOW: Color.fromhex("3B3232")
        },
        "terra": {
            Color.RED: Color.fromhex("8A7574"),
            Color.GREEN: Color.fromhex("252120"),
            Color.BLUE: Color.fromhex("E8CCCB"),
            Color.YELLOW: Color.fromhex("8A7574")
        },
        "dust": {
            Color.RED: Color.fromhex("989292"),
            Color.GREEN: Color.fromhex("2C2829"),
            Color.BLUE: Color.fromhex("FFFFFF"),
            Color.YELLOW: Color.fromhex("989292")
        },
        "brown": {
            Color.RED: Color.fromhex("522506"),
            Color.GREEN: Color.fromhex("000000"),
            Color.BLUE: Color.fromhex("905022"),
            Color.YELLOW: Color.fromhex("1C0C00")
        },
        "sky": {
            Color.RED: Color.fromhex("4EDEFD"),
            Color.GREEN: Color.fromhex("1C7E8F"),
            Color.BLUE: Color.fromhex("FFFFFF"),
            Color.YELLOW: Color.fromhex("4EDEFD")
        },
        "pink": {
            Color.RED: Color.fromhex("FD8B4E"),
            Color.GREEN: Color.fromhex("612400"),
            Color.BLUE: Color.fromhex("FFE0CE"),
            Color.YELLOW: Color.fromhex("FFB48F")
        },
        "casale": {
            Color.RED: Color.fromhex("FEFEFB"),
            Color.GREEN: Color.fromhex("161213"),
            Color.BLUE: Color.fromhex("5C5C5C"),
            Color.YELLOW: Color.fromhex("DF8F53")
        },
    },
}




class Image(Component):
    def __init__(self, components: dict[ImageLayer, ImageComponent] | pg.Surface, color_map: dict[Color, Color] = {}) -> None:
        if isinstance(components, pg.Surface):
            self.components = {ImageLayer.BASE: {"offset": (0, 0), "surface": components, "color_map": color_map}}
        else:
            self.components = components
        self.compose()

    def compose(self) -> None:
        if not self.components:
            raise ValueError("Cannot compose an image with no components")
        layers = sorted(self.components.keys(), key=lambda layer: layer.value)
        surface = self.components[layers[0]]["surface"].copy()
        for layer in layers[1:]:
            component = self.components[layer]
            x, y = component["offset"]
            if "color_map" in component:
                component_surface = Image.apply_color_map(component["surface"], component["color_map"])
            else:
                component_surface = component["surface"]
            surface.blit(component_surface, (x, y))
        self.surface = surface

    def set_at(self, x_y: tuple[int, int], color: _ColorInput) -> None:
        self.surface.set_at(x_y, color)

    def get_at(self, x_y: Sequence[int]) -> _RgbaOutput:
        return self.surface.get_at(x_y)
    
    def copy(self) -> Image:
        return Image(self.surface.copy())
    
    @classmethod
    def apply_color_map(cls, surface: pg.Surface, color_map: dict[Color, Color]) -> pg.Surface:
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                r, g, b, _ = surface.get_at((x, y))
                color = (r, g, b)
                if color in color_map:
                    new_color = color_map[color]
                    surface.set_at((x, y), new_color)
        return surface

class ImageTransitionStyle(str, Enum):
    LINEAR = auto()
    QUADRATIC = auto()
    CUBIC = auto()


@dataclass
class ImageTransition(Component):
    old_surface: pg.Surface
    new_surface: pg.Surface
    delay: float
    current_delay: float = 0.0
    transition: ImageTransitionStyle = ImageTransitionStyle.LINEAR
    reversed: bool = False


file_dir = os.path.dirname(os.path.realpath(__file__))

class HPBottleImageCollection(object):
    L0 = Image(pg.image.load(f"{file_dir}/../assets/bottles/hp0.png"))
    L1 = Image(pg.image.load(f"{file_dir}/../assets/bottles/hp1.png"))
    L2 = Image(pg.image.load(f"{file_dir}/../assets/bottles/hp2.png"))
    L3 = Image(pg.image.load(f"{file_dir}/../assets/bottles/hp3.png"))
    L4 = Image(pg.image.load(f"{file_dir}/../assets/bottles/hp4.png"))
    L5 = Image(pg.image.load(f"{file_dir}/../assets/bottles/hp5.png"))
    L6 = Image(pg.image.load(f"{file_dir}/../assets/bottles/hp6.png"))


class MPBottleImageCollection(object):
    L0 = Image(pg.image.load(f"{file_dir}/../assets/bottles/mp0.png"))
    L1 = Image(pg.image.load(f"{file_dir}/../assets/bottles/mp1.png"))
    L2 = Image(pg.image.load(f"{file_dir}/../assets/bottles/mp2.png"))
    L3 = Image(pg.image.load(f"{file_dir}/../assets/bottles/mp3.png"))
    L4 = Image(pg.image.load(f"{file_dir}/../assets/bottles/mp4.png"))
    L5 = Image(pg.image.load(f"{file_dir}/../assets/bottles/mp5.png"))
    L6 = Image(pg.image.load(f"{file_dir}/../assets/bottles/mp6.png"))

class SPBottleImageCollection(object):
    L0 = Image(pg.image.load(f"{file_dir}/../assets/bottles/sp0.png"))
    L1 = Image(pg.image.load(f"{file_dir}/../assets/bottles/sp1.png"))
    L2 = Image(pg.image.load(f"{file_dir}/../assets/bottles/sp2.png"))
    L3 = Image(pg.image.load(f"{file_dir}/../assets/bottles/sp3.png"))
    L4 = Image(pg.image.load(f"{file_dir}/../assets/bottles/sp4.png"))
    L5 = Image(pg.image.load(f"{file_dir}/../assets/bottles/sp5.png"))
    L6 = Image(pg.image.load(f"{file_dir}/../assets/bottles/sp6.png"))

class RegenerationBottleImageCollection(object):
    L0 = Image(pg.image.load(f"{file_dir}/../assets/bottles/reg0.png"))
    L1 = Image(pg.image.load(f"{file_dir}/../assets/bottles/reg1.png"))
    L2 = Image(pg.image.load(f"{file_dir}/../assets/bottles/reg2.png"))
    L3 = Image(pg.image.load(f"{file_dir}/../assets/bottles/reg3.png"))
    L4 = Image(pg.image.load(f"{file_dir}/../assets/bottles/reg4.png"))
    L5 = Image(pg.image.load(f"{file_dir}/../assets/bottles/reg5.png"))


class ImageCollection(object):
    EMPTY = Image(pg.Surface((0, 0), pg.SRCALPHA))
    BACKGROUND_NONE = Image(pg.Surface((28, 38), pg.SRCALPHA))
    BACKGROUND_SELECTED = Image(pg.image.load(f"{file_dir}/../assets/background_selected.png"))
    BACKGROUND_UNSELECTED = Image(pg.Surface((20, 38), pg.SRCALPHA))
    # CHARACTERS = {
    #     GenderType.FEMALE: {k: Image(pg.image.load(f"{file_dir}/../assets/characters/{k.lower()}_female.png")) for k in GameClassName},
    #     GenderType.MALE: {k: Image(pg.image.load(f"{file_dir}/../assets/characters/{k.lower()}_male.png")) for k in GameClassName},
    # }
    EMPTY_CAT_TEMPLATE = Image(pg.Surface((22, 22), pg.SRCALPHA))
    # CAT_TEMPLATE = Image(pg.image.load(f"{file_dir}/../assets/characters/cat_template.png"))
    # CAT_TEMPLATE_RARE = Image(pg.image.load(f"{file_dir}/../assets/characters/cat_template_rare.png"))

    RED_BOTTLE = HPBottleImageCollection()
    BLUE_BOTTLE = MPBottleImageCollection()
    GREEN_BOTTLE = SPBottleImageCollection()
    REGEN_BOTTLE = RegenerationBottleImageCollection()

class EquipImageCollection(object):
    SHIRTS = {
        Size.MEDIUM: {
            "white": Image(pg.image.load(f"{file_dir}/../assets/shirts/white_tight_male.png"))
        }
    }

    LEGS = {
        Size.MEDIUM: {
            "blue": Image(pg.image.load(f"{file_dir}/../assets/pants/blue_pants.png"))
        }
    }

    WEAPONS = {
        Size.SHORT: {
            "bow": Image(pg.image.load(f"{file_dir}/../assets/weapons/bow.png"))
        },
        Size.MEDIUM: {
            "bow": Image(pg.image.load(f"{file_dir}/../assets/weapons/bow.png"))
        },
        Size.TALL: {
            "bow": Image(pg.image.load(f"{file_dir}/../assets/weapons/bow.png"))
        },
        Size.LARGE: {
            "bow": Image(pg.image.load(f"{file_dir}/../assets/weapons/bow.png"))
        },
    }