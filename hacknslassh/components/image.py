from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum, auto
from typing import Sequence, Union

import pygame as pg

from .base import Component
from .description import GenderType, GameClassName

_ColorInput = Union[pg.Color, str, list[int], tuple[int, int, int], tuple[int, int, int, int]]
_RgbaOutput = tuple[int, int, int, int]


@dataclass
class Image(Component):
    surface: pg.Surface

    def set_at(self, x_y: tuple[int, int], color: _ColorInput) -> None:
        self.surface.set_at(x_y, color)

    def get_at(self, x_y: Sequence[int]) -> _RgbaOutput:
        return self.surface.get_at(x_y)
    
    def copy(self) -> Image:
        return Image(self.surface.copy())


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
    CHARACTERS = {
        GenderType.FEMALE: {k: Image(pg.image.load(f"{file_dir}/../assets/characters/{k.lower()}_female.png")) for k in GameClassName},
        GenderType.MALE: {k: Image(pg.image.load(f"{file_dir}/../assets/characters/{k.lower()}_male.png")) for k in GameClassName},
    }
    EMPTY_CAT_TEMPLATE = Image(pg.Surface((22, 22), pg.SRCALPHA))
    # CAT_TEMPLATE = Image(pg.image.load(f"{file_dir}/../assets/characters/cat_template.png"))
    # CAT_TEMPLATE_RARE = Image(pg.image.load(f"{file_dir}/../assets/characters/cat_template_rare.png"))

    RED_BOTTLE = HPBottleImageCollection()
    BLUE_BOTTLE = MPBottleImageCollection()
    GREEN_BOTTLE = SPBottleImageCollection()
    REGEN_BOTTLE = RegenerationBottleImageCollection()

    CAT_HEADS = {
        f"HEAD{str(i).zfill(2)}": Image(pg.image.load(f"{file_dir}/../assets/cats/head{str(i).zfill(2)}.png")) for i in range(10)
    }
    CAT_BODIES = {
        f"BODY{str(i).zfill(2)}": Image(pg.image.load(f"{file_dir}/../assets/cats/body{str(i).zfill(2)}.png")) for i in range(6)
    }
    CAT_TAILS = {
        f"TAIL{str(i).zfill(2)}": Image(pg.image.load(f"{file_dir}/../assets/cats/tail{str(i).zfill(2)}.png")) for i in range(3)
    }
    CAT_SITTING_BODIES = {
        f"SITTINGBODY{str(i).zfill(2)}": Image(pg.image.load(f"{file_dir}/../assets/cats/sittingbody{str(i).zfill(2)}.png")) for i in range(6)
    }

    SHIRTS = {
        "WHITE_MALE": Image(pg.image.load(f"{file_dir}/../assets/shirts/white_tight_male.png"))
    }
