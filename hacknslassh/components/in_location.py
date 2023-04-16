from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from hacknslassh.color_utils import Color
if TYPE_CHECKING:
    from hacknslassh.dungeon import Dungeon
from hacknslassh.components.base import Component

class Direction(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class Markers(object):
    ACTOR = {
        Direction.UP: "▲",
        Direction.DOWN: "▼",
        Direction.LEFT: "◀",
        Direction.RIGHT: "▶",
    }
    DOUBLE = {
        Direction.UP: "◢◣",
        Direction.DOWN: "◥◤",
        Direction.LEFT: "◀",
        Direction.RIGHT: "▶",
    }

@dataclass
class InLocation(Component):
    """
    Component for entities that are in a dungeon.
    """

    dungeon: Dungeon
    position: tuple[int, int, int] = (0, 0, 0)
    direction: Direction = Direction.UP
    marker: str = Markers.ACTOR[Direction.UP]
    fg: tuple[int, int, int] = Color.WHITE
    bg: tuple[int, int, int] | None = None
    own_fg: tuple[int, int, int] = Color.WHITE
    visibility: int = 255
    
    @property
    def forward(self) -> tuple[int, int, int]:
        delta_x = int(self.direction == Direction.DOWN) - int(self.direction == Direction.UP)
        delta_y = int(self.direction == Direction.RIGHT) - int(self.direction == Direction.LEFT)
        x, y, z = self.position
        return (x + delta_x, y + delta_y, z)
    
    @property
    def forward_below(self) -> tuple[int, int, int]:
        delta_x = int(self.direction == Direction.DOWN) - int(self.direction == Direction.UP)
        delta_y = int(self.direction == Direction.RIGHT) - int(self.direction == Direction.LEFT)
        x, y, z = self.position
        return (x + delta_x, y + delta_y, z-1)

    @property
    def above(self) -> tuple[int, int, int]:
        x, y, z = self.position
        return (x, y, z + 1)

    @property
    def below(self) -> tuple[int, int, int]:
        x, y, z = self.position
        return (x, y, z - 1)

    @property
    def floor(self) -> tuple[int, int, int]:
        x, y, z = self.position
        return (x, y, 0)

    @property
    def behind(self) -> tuple[int, int, int]:
        delta_x = int(self.direction == Direction.DOWN) - int(self.direction == Direction.UP)
        delta_y = int(self.direction == Direction.RIGHT) - int(self.direction == Direction.LEFT)
        x, y, z = self.position
        return (x - delta_x, y - delta_y, z)

    @property
    def right_side(self) -> tuple[int, int, int]:
        delta_x = int(self.direction == Direction.DOWN) - int(self.direction == Direction.UP)
        delta_y = int(self.direction == Direction.RIGHT) - int(self.direction == Direction.LEFT)
        x, y, z = self.position
        return (x - delta_y, y - delta_x, z)

    @property
    def left_side(self) -> tuple[int, int, int]:
        delta_x = int(self.direction == Direction.DOWN) - int(self.direction == Direction.UP)
        delta_y = int(self.direction == Direction.RIGHT) - int(self.direction == Direction.LEFT)
        x, y, z = self.position
        return (x + delta_y, y + delta_x, z)
    

if __name__ == "__main__":
    from dungeon import is_tile_shadowed_by_walls
    def shadow_string(xs, ys, walls):
        if xs == x0 and ys == y0:
            return "O"
        if is_tile_shadowed_by_walls((x0, y0), (xs, ys), walls): 
            if (xs, ys) in walls: 
                return "S"
            return "s"
        if (xs, ys) in walls: 
            return "w"
        return "_"

    sight_radius = 8
    
    
    x0, y0 = (0, -1)
    walls = [(1, i) for i in range(-4, 9)] + [(-1, i) for i in range(-4, 9)]
    walls.append((2, 0))
    N = 10
    rendered_map = [["" for y in range(y0-sight_radius, y0+sight_radius+1)] for x in range(x0-sight_radius, x0+sight_radius+1)]
    
    for xs in range(x0-sight_radius, x0+sight_radius+1):
        for ys in range(y0-sight_radius, y0+sight_radius+1):
            rendered_map[xs][ys] = shadow_string(xs, ys, walls)
    print("\n")
    import sys
    for xs in range(x0-sight_radius, x0+sight_radius+1):
        for ys in range(y0-sight_radius, y0+sight_radius+1):
            sys.stdout.write(rendered_map[xs][ys])
        sys.stdout.write("\n")

    print("\n")



    
