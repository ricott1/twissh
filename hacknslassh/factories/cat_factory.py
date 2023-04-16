from __future__ import annotations
from hashlib import sha256

import random
import uuid
from hacknslassh.components import acting, characteristics
from hacknslassh.components.base import Component
from hacknslassh.components.acting import Acting, Ai
from hacknslassh.components.description import ID, GameClassName, ActorInfo, GenderType, Language
from hacknslassh.components.image import Image, ImageCollection
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.rarity import Rarity
from hacknslassh.components.sight import Sight
from hacknslassh.components.tokens import BodyPartsDescriptor, CatchableToken, ColorDescriptor
from hacknslassh.db_connector import store
from hacknslassh.dungeon import Dungeon
from hacknslassh.color_utils import Color, ColorMix

male_cat_names = ["Punto", "Virgola", "Pepito", "Bibbiano", "Bibbi", "Bi", "Frufru", "Morover", "Lando", "Zetar", "Platone", "Gattoka"]
female_cat_names = ["Pepita", "Pepetta", "Bibbiana", "Matilda", "Mia", "Bibu", "Giovanna", "Seratonina", "Dopamina", "Bla-bla"]


def generate_cats(dungeon: Dungeon) -> list[list[Component]]:
    return [create_cat(dungeon, name, GenderType.MALE) for name in male_cat_names] + [create_cat(name, GenderType.FEMALE) for name in female_cat_names]

def create_cat(dungeon: Dungeon, name: str, gender: GenderType, should_store: bool = True) -> list[Component]:
    cat_id = uuid.uuid4().bytes[:12]
    age = random.randint(1, 12)
    rgb = characteristics.RGB.random()
    
    r = random.random()
    if r < 0.01:
        catchable_token = CatchableToken()
        rarity = Rarity.legendary()
        description = "A super wow cat!"
        colors = random.choice([ColorMix.SKY.value, ColorMix.PINK.value])
    elif r < 0.1:
        catchable_token = CatchableToken()
        rarity = Rarity.rare()
        description = "A wow cat!"
        colors = random.choice([ColorMix.CASALE.value, ColorMix.TERRA.value])
    elif r < 0.35:
        catchable_token = CatchableToken()
        rarity = Rarity.uncommon()
        description = "A cuter cat"
        colors = random.choice([ColorMix.BROWN.value, ColorMix.DUST.value])
    else:
        catchable_token = CatchableToken()
        rarity = Rarity.common()
        description = "A cute cat"
        colors = random.choice([ColorMix.ORANGE.value, ColorMix.GREY.value])

    seed = int.from_bytes(sha256(cat_id).digest())
    parts = (seed%len(ImageCollection.CAT_HEADS), seed%len(ImageCollection.CAT_BODIES), seed%len(ImageCollection.CAT_TAILS), 0, 0, 0)
    head = ImageCollection.CAT_HEADS["HEAD" + str(parts[0]).zfill(2)]
    body = ImageCollection.CAT_BODIES["BODY" + str(parts[1]).zfill(2)]
    sitting_body = ImageCollection.CAT_BODIES["BODY" + str(parts[1]).zfill(2)]
    tail = ImageCollection.CAT_TAILS["TAIL" + str(parts[2]).zfill(2)]
    image = ImageCollection.EMPTY_CAT_TEMPLATE.copy()
    image.surface.blit(body.surface, (3, 12))
    image.surface.blit(head.surface, (7, 3))
    image.surface.blit(tail.surface, (0, 3))
        
    for x in range(image.surface.get_width()):
        for y in range(image.surface.get_height()):
            r, g, b, a = image.surface.get_at((x, y))
            if a == 0:
                continue
            if (r, g, b) == Color.RED:
                image.surface.set_at((x, y), colors[0])
            elif (r, g, b) == Color.BLUE:
                image.surface.set_at((x, y), colors[1])
            elif (r, g, b) == Color.GREEN:
                image.surface.set_at((x, y), colors[2])
            elif (r, g, b) == Color.YELLOW:
                image.surface.set_at((x, y), colors[3])

    color_descriptor = ColorDescriptor(colors)
    body_parts = BodyPartsDescriptor(parts)
    if should_store:
        values = f'("{cat_id.hex()}", "{name}", "{age}", "{gender.value}", "{description}", "{rgb.red.value}", "{rgb.green.value}", "{rgb.blue.value}", "null", "{catchable_token.rarity}", "{color_descriptor.hex()}", "{body_parts.hex()}")'
        store("cats", values)

    pos_x, pos_y = dungeon.random_free_floor_tile()
    in_location = InLocation(dungeon, (pos_x, pos_y, 1), fg=rarity.color)
    x0, y0, _ = in_location.position
    sight = Sight.circle_sight()
    sight.update_visible_and_visited_tiles((x0, y0), in_location.direction, in_location.dungeon)
    return [
        ActorInfo(name, description, GameClassName.CAT, gender, [Language.GATTESE, Language.COMMON], age),
        ID(cat_id),
        rgb,
        catchable_token,
        color_descriptor,
        body_parts,
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

    cat_id = cat_data[0]
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
    
    color_descriptor = ColorDescriptor.from_hex(cat_data[10])

    colors = color_descriptor.colors
    
    parts = BodyPartsDescriptor.from_hex(cat_data[11]).parts
    head = ImageCollection.CAT_HEADS["HEAD" + str(parts[0]).zfill(2)]
    body = ImageCollection.CAT_BODIES["BODY" + str(parts[1]).zfill(2)]
    sitting_body = ImageCollection.CAT_BODIES["BODY" + str(parts[1]).zfill(2)]
    tail = ImageCollection.CAT_TAILS["TAIL" + str(parts[2]).zfill(2)]
    image = ImageCollection.EMPTY_CAT_TEMPLATE.copy()
    image.surface.blit(body.surface, (3, 12))
    image.surface.blit(head.surface, (7, 3))
    image.surface.blit(tail.surface, (0, 3))
        
    for x in range(image.surface.get_width()):
        for y in range(image.surface.get_height()):
            r, g, b, a = image.surface.get_at((x, y))
            if a == 0:
                continue
            if (r, g, b) == Color.RED:
                image.surface.set_at((x, y), colors[0])
            elif (r, g, b) == Color.BLUE:
                image.surface.set_at((x, y), colors[1])
            elif (r, g, b) == Color.GREEN:
                image.surface.set_at((x, y), colors[2])
            elif (r, g, b) == Color.YELLOW:
                image.surface.set_at((x, y), colors[3])
    rarity = Rarity(cat_data[9])
    pos_x, pos_y = dungeon.random_free_floor_tile()
    in_location = InLocation(dungeon, (pos_x, pos_y, 1), fg=rarity.color)
    x0, y0, _ = in_location.position
    sight = Sight.circle_sight()
    sight.update_visible_and_visited_tiles((x0, y0), in_location.direction, in_location.dungeon)
    
    return [
        ActorInfo(name, description, GameClassName.CAT, gender, [Language.GATTESE, Language.COMMON], age),
        ID(bytes.fromhex(cat_id)),
        rgb,
        CatchableToken(owner),
        color_descriptor,
        parts,
        image,
        acting,
        sight,
        Ai(),
        in_location,
        
    ]