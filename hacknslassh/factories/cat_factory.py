from __future__ import annotations
from hashlib import sha256

import random
import uuid
from hacknslassh.components import acting, characteristics
from hacknslassh.components.base import Component
from hacknslassh.components.acting import Acting, Ai
from hacknslassh.components.description import ID, GameClassName, ActorInfo, GenderType, Language
from hacknslassh.components.image import Image, ImageCollection, ImageLayer
from hacknslassh.components.in_location import ActiveMarkers, InLocation
from hacknslassh.components.rarity import Rarity
from hacknslassh.components.sight import Sight
from hacknslassh.components.tokens import  CatchableToken
from hacknslassh.db_connector import store
from hacknslassh.dungeon import Dungeon
import pygame as pg

from hacknslassh.processors.image_composer import random_image_from_game_class

male_cat_names = ["Punto", "Virgola", "Pepito", "Bibbiano", "Bibbi", "Bi", "Frufru", "Morover", "Lando", "Zetar", "Platone", "Gattoka"]
female_cat_names = ["Pepita", "Pepetta", "Bibbiana", "Matilda", "Mia", "Bibu", "Giovanna", "Seratonina", "Dopamina", "Bla-bla"]


def generate_cats(dungeon: Dungeon) -> list[list[Component]]:
    return [create_cat(dungeon, name, GenderType.MALE) for name in male_cat_names] + [create_cat(dungeon, name, GenderType.FEMALE) for name in female_cat_names]

def create_cat(dungeon: Dungeon, name: str, gender: GenderType, should_store: bool = True) -> list[Component]:
    cat_id = uuid.uuid4().bytes
    age = random.randint(1, 12)
    rgb = characteristics.RGB.random()
    
    r = random.random()
    if r < 0.01:
        catchable_token = CatchableToken()
        rarity = Rarity.legendary()
        description = "A super wow cat!"
    elif r < 0.1:
        catchable_token = CatchableToken()
        rarity = Rarity.rare()
        description = "A wow cat!"
    elif r < 0.35:
        catchable_token = CatchableToken()
        rarity = Rarity.uncommon()
        description = "A cuter cat"
    else:
        catchable_token = CatchableToken()
        rarity = Rarity.common()
        description = "A cute cat"

    seed = sha256(cat_id).digest()
    image = random_image_from_game_class(GameClassName.CAT, gender.value.to_bytes() + seed)

    if should_store:
        values = f'("{cat_id.hex()}", "{name}", "{age}", "{gender.value}", "{description}", "{rgb.red.value}", "{rgb.green.value}", "{rgb.blue.value}", "null", "{rarity.level.value}")'
        store("cats", values)

    pos_x, pos_y = dungeon.random_free_floor_tile()
    in_location = InLocation.Actor(dungeon, (pos_x, pos_y, 1), fg=rarity.color)
    x0, y0, _ = in_location.position
    sight = Sight.circle_sight()
    sight.update_visible_and_visited_tiles((x0, y0), in_location.direction, in_location.dungeon)
    return [
        ActorInfo(name, description, GameClassName.CAT, gender, [Language.GATTESE, Language.COMMON], age),
        ID(cat_id),
        rgb,
        catchable_token,
        image,
        Acting.default(),
        sight,
        Ai(),
        in_location,
        rarity
    ]

def load_cat(dungeon: Dungeon, cat_data: tuple) -> list[Component]:
    acting = Acting.default()
    sight = Sight.circle_sight()

    cat_id = bytes.fromhex(cat_data[0])
    name = cat_data[1]
    age = cat_data[2]
    gender = [GenderType.MALE, GenderType.FEMALE][int(cat_data[3])]
    description = cat_data[4]
    rgb = characteristics.RGB(
        characteristics.ColorCharacteristic(cat_data[5]),
        characteristics.ColorCharacteristic(cat_data[6]),
        characteristics.ColorCharacteristic(cat_data[7])
    )
    owner = cat_data[8]
    if owner == "null":
        owner = None
    
    seed = sha256(cat_id).digest()
    image = random_image_from_game_class(GameClassName.CAT, gender.value.to_bytes() + seed)

    rarity = Rarity(cat_data[9])
    pos_x, pos_y = dungeon.random_free_floor_tile()
    in_location = InLocation.Actor(dungeon, (pos_x, pos_y, 1), fg=rarity.color)
    x0, y0, _ = in_location.position
    sight = Sight.circle_sight()
    sight.update_visible_and_visited_tiles((x0, y0), in_location.direction, in_location.dungeon)
    
    return [
        ActorInfo(name, description, GameClassName.CAT, gender, [Language.GATTESE, Language.COMMON], age),
        ID(cat_id),
        rgb,
        CatchableToken(owner),
        image,
        acting,
        sight,
        Ai(),
        in_location,
        rarity
    ]