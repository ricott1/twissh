from __future__ import annotations
from hashlib import sha256

import random
import uuid
import esper
from hacknslassh.components import acting, characteristics
from hacknslassh.components.base import Component
from hacknslassh.components.description import GameClassName, Info, GenderType, Language
from hacknslassh.components.image import Image, ImageCollection
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.sight import Sight
from hacknslassh.components.tokens import BodyPartsDescriptor, CatchableToken, ColorDescriptor
from hacknslassh.dungeon import Dungeon
from hacknslassh.color_utils import Color, ColorMix

male_cat_names = ["Punto", "Virgola", "Pepito", "Bibbiano", "Bibbi", "Bi", "Frufru", "Morover", "Lando", "Zetar", "Platone", "Gattoka"]
female_cat_names = ["Pepita", "Pepetta", "Bibbiana", "Matilda", "Mia", "Bibu", "Giovanna", "Seratonina", "Dopamina", "Bla-bla"]


def generate_cats() -> list[dict[str, Component]]:
    return [create_cat(name, GenderType.MALE) for name in male_cat_names] + [create_cat(name, GenderType.FEMALE) for name in female_cat_names]

def create_cat(name: str, gender: GenderType) -> int:
    cat_id = uuid.uuid4().bytes[:12]
    age = random.randint(1, 12)
    
    _rgb = characteristics.RGB.random()
    
    r = random.random()
    if r < 0.01:
        _catchable_token = CatchableToken(rarity=3)
        description = "A super wow cat!"
        _colors = random.choice([ColorMix.SKY.value, ColorMix.PINK.value])
    elif r < 0.1:
        _catchable_token = CatchableToken(rarity=2)
        description = "A wow cat!"
        _colors = random.choice([ColorMix.CASALE.value, ColorMix.TERRA.value])
    elif r < 0.35:
        _catchable_token = CatchableToken(rarity=1)
        description = "A cuter cat"
        _colors = random.choice([ColorMix.BROWN.value, ColorMix.DUST.value])
    else:
        _catchable_token = CatchableToken(rarity=0)
        description = "A cute cat"
        _colors = random.choice([ColorMix.ORANGE.value, ColorMix.GREY.value])

    seed = int.from_bytes(sha256(cat_id).digest())
    _parts = (seed%len(ImageCollection.CAT_HEADS), seed%len(ImageCollection.CAT_BODIES), seed%len(ImageCollection.CAT_TAILS), 0, 0, 0)

    return {
        "info": Info(name, description, GameClassName.CAT.value, gender, [Language.GATTESE, Language.COMMON], age, cat_id),
        "rgb": _rgb,
        "catchableToken": _catchable_token,
        "ColorDescriptor": ColorDescriptor(_colors),
        "BodyPartsDescriptor": BodyPartsDescriptor(_parts),
    }  

def load_cat(world: esper.World, dungeon: Dungeon, cat_data: tuple) -> int:
    x, y = dungeon.random_free_floor_tile()
    _acting = acting.Acting()
    _sight = Sight.circle_sight()

    _in_location = InLocation(dungeon, (x, y, 1), fg=(255, 0, 0))
    
    _sight.update_visible_and_visited_tiles((x, y), _in_location.direction, dungeon)

    cat_id = cat_data[0]
    name = cat_data[1]
    age = cat_data[2]
    _gender = [GenderType.MALE, GenderType.FEMALE][int(cat_data[3])]
    description = cat_data[4]
    _rgb = characteristics.RGB(
        characteristics.ColorCharacteristic(cat_data[5]),
        characteristics.ColorCharacteristic(cat_data[6]),
        characteristics.ColorCharacteristic(cat_data[7])
    )
    _owner = cat_data[8]
    if _owner == "null":
        _owner = None
    
    _rarity = cat_data[9]
    
    _color_descriptor = ColorDescriptor.from_hex(cat_data[10])
    _colors = _color_descriptor.colors
    
    parts = BodyPartsDescriptor.from_hex(cat_data[11]).parts
    head = ImageCollection.CAT_HEADS["HEAD" + str(parts[0]).zfill(2)]
    body = ImageCollection.CAT_BODIES["BODY" + str(parts[1]).zfill(2)]
    sitting_body = ImageCollection.CAT_BODIES["BODY" + str(parts[1]).zfill(2)]
    tail = ImageCollection.CAT_TAILS["TAIL" + str(parts[2]).zfill(2)]
    _image = ImageCollection.EMPTY_CAT_TEMPLATE.copy()
    _image.surface.blit(body.surface, (3, 12))
    _image.surface.blit(head.surface, (7, 3))
    _image.surface.blit(tail.surface, (0, 3))
        
    for _x in range(_image.surface.get_width()):
        for _y in range(_image.surface.get_height()):
            r, g, b, a = _image.surface.get_at((_x, _y))
            if a == 0:
                continue
            if (r, g, b) == Color.RED:
                _image.surface.set_at((_x, _y), _colors[0])
            elif (r, g, b) == Color.BLUE:
                _image.surface.set_at((_x, _y), _colors[1])
            elif (r, g, b) == Color.GREEN:
                _image.surface.set_at((_x, _y), _colors[2])
            elif (r, g, b) == Color.YELLOW:
                _image.surface.set_at((_x, _y), _colors[3])
    
    _components = [
        _image,
        _rgb,
        Info(name, description, GameClassName.CAT.value, _gender, [Language.GATTESE, Language.COMMON], age, bytes.fromhex(cat_id)),
        _acting,
        _sight,
        _in_location,
        acting.Ai(),
        CatchableToken(_owner, _rarity),
        _color_descriptor,
        parts
    ]
    return world.create_entity(*_components)