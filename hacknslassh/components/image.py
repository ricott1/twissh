from enum import Enum, auto
from .base import Component
import pygame as pg
import os
from dataclasses import dataclass

from .info import RaceType, GenderType


@dataclass
class Image(Component):
    surface: pg.Surface


class ImageTransitionStyle(str, Enum):
    LINEAR = auto()
    QUADRATIC = auto()
    CUBIC = auto()
    
@dataclass
class ImageTransition(Component):
    old_surface: pg.Surface
    new_surface: pg.Surface
    delay: float = 2.0
    current_delay: float = 0.0
    transition: ImageTransitionStyle = ImageTransitionStyle.LINEAR
    reversed: bool = False

file_dir = os.path.dirname(os.path.realpath(__file__))


class HPPotionImageCollection(object):
    LARGE = Image(pg.image.load(f"{file_dir}/assets/potions/hp_large.png"))
    MEDIUM = Image(pg.image.load(f"{file_dir}/assets/potions/hp_medium.png"))
    SMALL = Image(pg.image.load(f"{file_dir}/assets/potions/hp_small.png"))


class MPPotionImageCollection(object):
    LARGE = Image(pg.image.load(f"{file_dir}/assets/potions/mp_large.png"))
    MEDIUM = Image(pg.image.load(f"{file_dir}/assets/potions/mp_medium.png"))
    SMALL = Image(pg.image.load(f"{file_dir}/assets/potions/mp_small.png"))


class RejuvenationPotionImageCollection(object):
    LARGE = Image(pg.image.load(f"{file_dir}/assets/potions/rejuvenation_large.png"))
    MEDIUM = Image(pg.image.load(f"{file_dir}/assets/potions/rejuvenation_medium.png"))
    SMALL = Image(pg.image.load(f"{file_dir}/assets/potions/rejuvenation_small.png"))


class CurePotionImageCollection(object):
    LARGE = Image(pg.image.load(f"{file_dir}/assets/potions/cure_large.png"))
    MEDIUM = Image(pg.image.load(f"{file_dir}/assets/potions/cure_medium.png"))
    SMALL = Image(pg.image.load(f"{file_dir}/assets/potions/cure_small.png"))


class HPBottleImageCollection(object):
    L0 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp0.png"))
    L1 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp1.png"))
    L2 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp2.png"))
    L3 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp3.png"))
    L4 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp4.png"))
    L5 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp5.png"))
    L6 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp6.png"))
    R0 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp_reg0.png"))
    R1 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp_reg1.png"))
    R2 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp_reg2.png"))
    R3 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp_reg3.png"))
    R4 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp_reg4.png"))
    R5 = Image(pg.image.load(f"{file_dir}/assets/bottles/hp_reg5.png"))


class MPBottleImageCollection(object):
    L0 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp0.png"))
    L1 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp1.png"))
    L2 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp2.png"))
    L3 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp3.png"))
    L4 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp4.png"))
    L5 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp5.png"))
    L6 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp6.png"))
    R0 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp_reg0.png"))
    R1 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp_reg1.png"))
    R2 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp_reg2.png"))
    R3 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp_reg3.png"))
    R4 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp_reg4.png"))
    R5 = Image(pg.image.load(f"{file_dir}/assets/bottles/mp_reg5.png"))


class ImageCollection(object):
    EMPTY = Image(pg.Surface((0, 0), pg.SRCALPHA))
    BACKGROUND_NONE = Image(pg.image.load(f"{file_dir}/assets/background_none.png"))
    BACKGROUND_SELECTED = Image(pg.image.load(f"{file_dir}/assets/background_selected.png"))
    BACKGROUND_UNSELECTED = Image(pg.image.load(f"{file_dir}/assets/background_unselected.png"))
    CHARACTERS = {
        GenderType.FEMALE: {
            k: Image(pg.image.load(f"{file_dir}/assets/characters/{k.lower()}_female.png")) for k in RaceType
        },
        GenderType.MALE: {
            k: Image(pg.image.load(f"{file_dir}/assets/characters/{k.lower()}_male.png")) for k in RaceType
        },
    }

    HP_BOTTLE = HPBottleImageCollection()
    MP_BOTTLE = MPBottleImageCollection()
    HP_POTION = HPPotionImageCollection()
    MP_POTION = MPPotionImageCollection()
    REJUVENATION_POTION = RejuvenationPotionImageCollection()
    CURE_POTION = CurePotionImageCollection()
