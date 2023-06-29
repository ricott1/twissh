from __future__ import annotations

import random
from hacknslassh.components.characteristics import RGB, ColorCharacteristic
from hacknslassh.components.acting import Acting
from hacknslassh.components.base import Component
from hacknslassh.components.description import ID, GameClassName, ActorInfo, GenderType, Language
from hacknslassh.components.equipment import Equipment
from hacknslassh.components.image import Image, ImageCollection
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.item import QuickItems
from hacknslassh.components.sight import Sight
from hacknslassh.components.user import User
from hacknslassh.constants import KeyMap
from hacknslassh.db_connector import store
from hacknslassh.dungeon import Dungeon
from hacknslassh.processors.dig_actions import Dig
from hacknslassh.processors.transform_actions import TransformIntoRandom
from web.server import UrwidMind

from hacknslassh.processors.image_composer import random_image_from_game_class

male_names = (
    "Gorbacioff",
    "Gundam",
    "Lukiko",
    "Armando",
    "Formaggio",
    "Pancrazio",
    "Tancredi",
    "Swallace",
    "Pertis",
    "Pericles",
    "Atheno",
    "Mastella",
    "Ciriaco",
    "Harri",
    "Pantera",
)

female_names = (
    "Annarella",
    "Giovanna",
    "Giovannella",
    "Samantha",
    "Arouen",
    "Jeffyel",

)


def create_player(mind: UrwidMind, dungeon: Dungeon, gender: GenderType, game_class: GameClassName, should_store: bool = True) -> list[Component]:
    acting = Acting.default()
    
    if game_class == GameClassName.ELF:
        sight = Sight.true_sight()
    else:
        sight = Sight.cone_sight()

    x, y = dungeon.random_free_floor_tile()
    in_location = InLocation.Actor(dungeon, (x, y, 1), fg=(255, 0, 0))
    sight.update_visible_and_visited_tiles((x, y), in_location.direction, in_location.dungeon)
    # if game_class == GameClassName.HUMAN:
    #     acting.actions["t"] = TransformIntoDevil()
    if game_class == GameClassName.DWARF:
        acting.actions[KeyMap.DIG] = Dig()
    elif game_class == GameClassName.ORC:
        acting.actions[KeyMap.TRANSFORM] = TransformIntoRandom()

    name = random.sample(male_names, 1)[0] if gender == GenderType.MALE else random.sample(female_names, 1)[0]
    age = random.randint(16, 48)
    rgb = RGB.random()
    
    if should_store:
        values = f'("{mind.avatar.uuid.hex}", "{name}", "{age}", "{gender.value}", "{game_class}", "{rgb.red.value}", "{rgb.green.value}", "{rgb.blue.value}")'
        store("players", values)

    image = random_image_from_game_class(game_class, gender.value.to_bytes() + mind.avatar.uuid.bytes)
    
    return [
        image,
        rgb,
        ActorInfo(name, "description", game_class, gender, [Language.COMMON], age),
        ID(mind.avatar.uuid.bytes),
        sight,
        acting,
        User(mind),
        QuickItems(),
        Equipment(),
        in_location
    ]

  
def load_player(mind: UrwidMind, dungeon: Dungeon, player_data: tuple) -> list[Component]:
    player_id = player_data[0]
    gender = GenderType.MALE if player_data[3] == 1 else GenderType.FEMALE
    game_class = GameClassName(player_data[4])
    
    rgb = RGB(
        ColorCharacteristic(player_data[5]), 
        ColorCharacteristic(player_data[6]),
        ColorCharacteristic(player_data[7])
    )
    acting = Acting.default()
    
    if game_class == GameClassName.ELF:
        sight = Sight.true_sight()
    else:
        sight = Sight.cone_sight()

    x, y = dungeon.random_free_floor_tile()    
    in_location = InLocation.Actor(dungeon, (x, y, 1), fg=(255, 0, 0))
    sight.update_visible_and_visited_tiles((x, y), in_location.direction, in_location.dungeon)
    # if game_class == GameClassName.HUMAN:
    #     acting.actions["t"] = TransformIntoDevil()
    if game_class == GameClassName.DWARF:
        acting.actions[KeyMap.DIG] = Dig()
    # elif game_class == GameClassName.DEVIL:
    #     acting.actions["r"] = IncreaseSightRadius()
    #     rgb = characteristics.RGB.devil()
    elif game_class == GameClassName.ORC:
        acting.actions[KeyMap.TRANSFORM] = TransformIntoRandom()

    image = random_image_from_game_class(game_class, gender.value.to_bytes() + player_id)
    
    return [
        image,
        rgb,
        ActorInfo(player_data[1], "description", game_class, gender, [Language.COMMON], player_data[2]),
        ID(player_id),
        sight,
        acting,
        User(mind),
        QuickItems(),
        Equipment(),
        in_location
    ]