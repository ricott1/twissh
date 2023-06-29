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

class ActiveMarkers:
    ACTOR = {
        Direction.UP: "▲",
        Direction.DOWN: "▼",
        Direction.LEFT: "◀",
        Direction.RIGHT: "▶",
    }
    ATTACK = {
        Direction.UP: "⩓",
        Direction.DOWN: "⩔",
        Direction.LEFT: "⪡",
        Direction.RIGHT: "⪢"
    }
    PARRY = {
        Direction.UP: "▀",
        Direction.DOWN: "▄",
        Direction.LEFT: "▌",
        Direction.RIGHT: "▐"
    }
    DEATH = {
        Direction.UP: "X",
        Direction.DOWN: "X",
        Direction.LEFT: "X",
        Direction.RIGHT: "X"
    }
    ARROW = {
        Direction.UP: "↑",
        Direction.DOWN: "↓",
        Direction.LEFT: "←",
        Direction.RIGHT: "→"
    }
    WALL = {Direction.UP: "█"}
    POTION = {Direction.UP: "u"}
    EQUIPMENT = {Direction.UP: "e"}


@dataclass
class InLocation(Component):
    """
    Component for entities that are in a dungeon.
    """

    dungeon: Dungeon
    active_markers: dict[Direction, str]
    position: tuple[int, int, int] = (0, 0, 0)
    direction: Direction = Direction.UP
    fg: tuple[int, int, int] = Color.WHITE
    bg: tuple[int, int, int] | None = None
    visibility: int = 255

    @property
    def marker(self) -> str:
        return self.active_markers[self.direction]
    
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
    
    @classmethod
    def Actor(cls, dungeon: Dungeon, position: tuple[int, int, int], fg: tuple[int, int, int] = Color.WHITE) -> InLocation:
        return cls(dungeon, ActiveMarkers.ACTOR, position = position, fg = fg)
    
    @classmethod
    def Wall(cls, dungeon: Dungeon, position: tuple[int, int, int]) -> InLocation:
        return cls(dungeon, ActiveMarkers.WALL, position = position)
    
    @classmethod
    def Potion(cls, dungeon: Dungeon, position: tuple[int, int, int], fg: tuple[int, int, int] = Color.WHITE) -> InLocation:
        return cls(dungeon, ActiveMarkers.POTION, position = position, fg = fg)
    
    @classmethod
    def Arrow(cls, dungeon: Dungeon, position: tuple[int, int, int], direction: Direction = Direction.UP) -> InLocation:
        return cls(dungeon, ActiveMarkers.ARROW, position = position, direction = direction)
    
    @classmethod
    def Equipment(cls, dungeon: Dungeon, position: tuple[int, int, int], fg: tuple[int, int, int] = Color.WHITE) -> InLocation:
        return cls(dungeon, ActiveMarkers.EQUIPMENT, position = position, fg = fg)

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



    
