
from hacknslassh.processors.dig_actions import Dig
from hacknslassh.processors.transform_actions import TransformIntoCat, TransformIntoDevil
from hacknslassh.utils import random_name

from .base import *
from .characteristics import *
from .description import *
from .in_location import *
from .image import *
from .item import *
from .user import *
from .acting import *
from .utils import *
from .sight import *



def get_components_for_game_class(mind: UrwidMind, dungeon, gender: GenderType, game_class: GameClassName) -> list[Component]:
    x, y = dungeon.random_floor_tile()
    _acting = acting.Acting()
    
    if game_class == GameClassName.ELF:
        _sight = Sight.true_sight()
    else:
        _sight = Sight()

    _in_location = InLocation(dungeon, (x, y, 1), fg=(255, 0, 0))
    _sight.update_visible_and_visited_tiles((x, y), _in_location.direction, dungeon)

    if game_class == GameClassName.HUMAN:
        _acting.actions["t"] = TransformIntoDevil()
        _rgb = characteristics.RGB.human()
    elif game_class == GameClassName.DWARF:
        _acting.actions["d"] = Dig()
        _rgb = characteristics.RGB.dwarf()
    # elif game_class == GameClassName.DEVIL:
    #     _acting.actions["r"] = IncreaseSightRadius()
    #     _rgb = characteristics.RGB.devil()
    elif game_class == GameClassName.ORC:
        _acting.actions["t"] = TransformIntoCat()
        _rgb = characteristics.RGB.orc()
    elif game_class == GameClassName.ELF:
        _rgb = characteristics.RGB.elf()

    _components = [
        ImageCollection.CHARACTERS[gender][game_class],
        _rgb,
        Info(random_name(), "description", game_class, gender, [Language.COMMON]),
        _in_location,
        _sight,
        _acting,
        User(mind)
    ]
    return _components
