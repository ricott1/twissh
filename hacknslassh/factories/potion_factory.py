from __future__ import annotations
from enum import Enum, auto
import os
import esper

import pygame as pg
from hacknslassh.color_utils import Color
from hacknslassh.components.characteristics import RGB
from hacknslassh.components.base import Component
from hacknslassh.components.image import Image, ImageCollection
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.rarity import Rarity
from hacknslassh.components.item import ConsumableItem, ItemInfo
from hacknslassh.components.user import User
from hacknslassh.db_connector import store
from hacknslassh.dungeon import Dungeon
from web.server import UrwidMind

class PotionSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    MAX = "max"

class PotionColor(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    WHITE = "white"

file_dir = os.path.dirname(os.path.realpath(__file__))

def apply_potion(world: esper.World, ent_id: int, color: PotionColor, size: PotionSize) -> None:
    rgb = world.try_component(ent_id, RGB)
    if not rgb:
        return
    if size == PotionSize.SMALL:
        value = 30
    elif size == PotionSize.MEDIUM:
        value = 90
    elif size == PotionSize.LARGE:
        value = 150
    elif size == PotionSize.MAX:
        value = 255 * 3

    if color == PotionColor.RED:
        rgb.red.value += value
    elif color == PotionColor.GREEN:
        rgb.green.value += value
    elif color == PotionColor.BLUE:
        rgb.blue.value += value
    elif color == PotionColor.PURPLE:
        rgb.red.value += value//2
        rgb.blue.value += value//2
    elif color == PotionColor.WHITE:
        rgb.red.value += value//3
        rgb.green.value += value//3
        rgb.blue.value += value//3
    
    if user:= world.try_component(ent_id, User):
        user.mind.process_event("player_rgb_changed")

def create_potion(dungeon: Dungeon, color: PotionColor, size: PotionSize, should_store: bool = False) -> list[Component]:
    effect = lambda world, ent_id: apply_potion(world, ent_id, color, size)
    info = ItemInfo(f"Potion", f"A {size.value} {color.value} potion")
    if size == PotionSize.SMALL:
        item_rarity = Rarity.common()
    elif size == PotionSize.MEDIUM:
        item_rarity = Rarity.common()
    elif size == PotionSize.LARGE:
        item_rarity = Rarity.uncommon()
    elif size == PotionSize.MAX:
        item_rarity = Rarity.rare()

    x, y = dungeon.random_free_floor_tile()
    return [
        Image(pg.image.load(f"{file_dir}/../assets/potions/{color.value}_{size.value}.png")),
        ConsumableItem(effect),
        info,
        item_rarity,
        InLocation(dungeon, (x, y, 0), marker="u", fg=getattr(Color, color.value.upper()))
    ]
