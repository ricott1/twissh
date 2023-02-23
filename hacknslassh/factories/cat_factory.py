from __future__ import annotations
from enum import Enum

import random
import esper
from hacknslassh.components import acting, characteristics
from hacknslassh.components.description import GameClassName, Info, GenderType, Language
from hacknslassh.components.image import Image, ImageCollection
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.sight import Sight
from hacknslassh.components.tokens import CatchableToken
from hacknslassh.dungeon import Dungeon
from hacknslassh.constants import Color


cat_names = ["Punto", "Virgola", "Pepito", "Pepita", "Pepetta", "Pepetto", "Bibbiano", "Bibbiana"]


# public Color generateRandomColor(Color mix) {
#   Random random = new Random();
#   int red = random.nextInt(256);
#   int green = random.nextInt(256);
#   int blue = random.nextInt(256);

#   // mix the color
#   if (mix != null) {
#       red = (red + mix.getRed()) / 2;
#       green = (green + mix.getGreen()) / 2;
#       blue = (blue + mix.getBlue()) / 2;
#   }

#   Color color = new Color(red, green, blue);
#   return color;
# }

def generate_color(mix: Color = Color.WHITE) -> Color:
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)

    red = (red + mix[0]) // 2
    green = (green + mix[1]) // 2
    blue = (blue + mix[2]) // 2

    return (red, green, blue)

def create_cat(world: esper.World, dungeon: Dungeon) -> int:
    x, y = dungeon.random_free_floor_tile()
    _acting = acting.Acting()
    _sight = Sight.circle_sight()

    _in_location = InLocation(dungeon, (x, y, 1), fg=(255, 0, 0))
    
    _sight.update_visible_and_visited_tiles((x, y), _in_location.direction, dungeon)
    _gender = random.choice([GenderType.MALE, GenderType.FEMALE])
    _image = ImageCollection.CAT_TEMPLATE.copy()
    primary_color = Color.random()
    _colors = [primary_color]
    for _ in range(3):
        while (col := Color.random()) == primary_color:
            pass
        _colors.append(col)
    _colors.append(Color.BLACK if primary_color != Color.BLACK else Color.YELLOW)

    # FIXME: this could be optmized
    for _x in range(_image.surface.get_width()):
        for _y in range(_image.surface.get_height()):
            r, g, b, a = _image.surface.get_at((_x, _y))
            if a == 0:
                continue
            if (r, g, b) == Color.RED:
                _image.surface.set_at((_x, _y), _colors[0].value)
            elif (r, g, b) == Color.BLUE:
                _image.surface.set_at((_x, _y), _colors[1].value)
            elif (r, g, b) == Color.GREEN:
                _image.surface.set_at((_x, _y), _colors[2].value)
            elif (r, g, b) == Color.YELLOW:
                _image.surface.set_at((_x, _y), _colors[3].value)
            elif (r, g, b) == Color.BLACK:
                _image.surface.set_at((_x, _y), _colors[4].value)
    
    _components = [
        _image,
        characteristics.RGB.random(),
        Info(random.choice(cat_names), "A random cat.", GameClassName.CAT.value, _gender, [Language.GATTESE, Language.COMMON]),
        _acting,
        _sight,
        _in_location,
        acting.Ai(),
        CatchableToken()
    ]
    return world.create_entity(*_components)