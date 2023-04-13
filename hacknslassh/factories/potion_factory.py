from __future__ import annotations
from enum import Enum, auto
import os
import esper

import pygame as pg
from hacknslassh.components.characteristics import RGB, ColorCharacteristic
from hacknslassh.components.acting import Acting
from hacknslassh.components.base import Component
from hacknslassh.components.description import ID, GameClassName, ActorInfo, GenderType, Language
from hacknslassh.components.image import Image, ImageCollection
from hacknslassh.components.item import ConsumableItem, ItemRarity
from hacknslassh.db_connector import store
from hacknslassh.processors.catch_action import Catch
from hacknslassh.processors.dig_actions import Dig
from hacknslassh.processors.transform_actions import TransformIntoRandom
from web.server import UrwidMind

class PotionSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class PotionColor(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    WHITE = "white"

file_dir = os.path.dirname(os.path.realpath(__file__))

def apply_potion(world: esper.World, ent_id: int, color: PotionColor, size: PotionSize) -> None:
    if size == PotionSize.SMALL:
        value = 10
    elif size == PotionSize.MEDIUM:
        value = 25
    elif size == PotionSize.LARGE:
        value = 50

    if rgb := world.try_component(ent_id, RGB):
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

def create_potion(color: PotionColor, size: PotionSize, should_store: bool = False) -> list[Component]:
    effect = lambda world, ent_id: apply_potion(world, ent_id, color, size)
    if size == PotionSize.SMALL:
        item_rarity = ItemRarity.common()
    elif size == PotionSize.MEDIUM:
        item_rarity = ItemRarity.uncommon()
    elif size == PotionSize.LARGE:
        item_rarity = ItemRarity.rare()

    return [
        Image(pg.image.load(f"{file_dir}/assets/potions/{color.value}_{size.value}.png")),
        ConsumableItem(effect),
        item_rarity,
    ]
