
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from hacknslassh.dungeon import Dungeon

from hacknslassh.components.in_location import Direction
from hacknslassh.components.base import Component
from hacknslassh.utils import distance

MAX_SIGHT_RADIUS = 20

class SightShape(str, Enum):
    CIRCLE = "circle"
    # SQUARE = "square"
    CONE = "cone"
    TRUE = "true"

class SightShapeIcons(str, Enum):
    CIRCLE = "○"
    # SQUARE = "□"
    CONE = "△"
    TRUE = "◉"

@dataclass
class Sight(Component):
    _radius: int = 9
    color: tuple[int, int, int] = (255, 255, 255)
    shape: SightShape = SightShape.CONE

    @property
    def radius(self) -> int:
        return self._radius
    
    @radius.setter
    def radius(self, value: int) -> None:
        self._radius = min(MAX_SIGHT_RADIUS, max(0, value))

    @property
    def icon(self) -> str:
        for shape, icon in zip(SightShape, SightShapeIcons):
            if self.shape == shape:
                return icon
        return "?"
    
    @classmethod
    def cat_sight(cls) -> Sight:
        return cls(10, (255, 255, 255), SightShape.CIRCLE)
    
    @classmethod
    def true_sight(cls) -> Sight:
        return cls(15, (255, 255, 255), SightShape.TRUE)

    def __post_init__(self) -> None:
        self.visited_tiles = {}
        self.visible_tiles = {}
        # self.update_visible_and_visited_tiles()

    def update_visible_and_visited_tiles(self, x_y0: tuple[int, int], direction: Direction, dungeon: Dungeon) -> None:
        x0, y0 = x_y0
        # Using a dict ensures that entries are ordered by smallest distance first.
        self.visible_tiles = {}
        if self.shape == SightShape.TRUE:
            for tile in dungeon.all_visible_tiles_at(x0, y0):
                x, y, _ = tile
                self.visible_tiles[(x, y)] = None
        else:
            for tile in dungeon.visible_tiles_at(x0, y0):
                if self.is_tile_visible(tile, direction, (x0, y0)):
                    x, y, _ = tile
                    self.visible_tiles[(x, y)] = None

        self.visited_tiles.update(self.visible_tiles)


    def is_tile_visible(self, tile: tuple[int, int, float], direction: Direction, x0_y0: tuple[int, int]) -> bool:
        x, y, d = tile
        x0, y0 = x0_y0
        if d <= self.radius:
            if self.shape == SightShape.CIRCLE:
                return True
            if self.shape == SightShape.CONE:
                if (direction == Direction.RIGHT and y >= y0 and y0-y <= abs(x-x0) <= y-y0)\
                or (direction == Direction.LEFT and y <= y0 and y-y0 <= abs(x-x0) <= y0-y)\
                or (direction == Direction.DOWN and x >= x0 and x0-x <= abs(y-y0) <= x-x0)\
                or (direction == Direction.UP and x <= x0 and x-x0 <= abs(y-y0) <= x0-x):
                    return True
        # if self.shape == SightShape.SQUARE:
        #     if max(abs(x0 - x), abs(y0 -y)) <= self.radius:
        #         return True
        return False