
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
    shape: SightShape

    def __post_init__(self) -> None:
        self._radius = 1
        self.color = (255, 255, 255)
        self.visited_tiles = {}
        self.visible_tiles = {}

    @property
    def radius(self) -> int:
        return self._radius
    
    @radius.setter
    def radius(self, value: int) -> None:
        self._radius = min(MAX_SIGHT_RADIUS, max(1, value))

    @property
    def icon(self) -> str:
        for shape, icon in zip(SightShape, SightShapeIcons):
            if self.shape == shape:
                return icon
        return "?"
    
    @classmethod
    def true_sight(cls) -> Sight:
        return cls(SightShape.TRUE)

    def update_visible_and_visited_tiles(self, x_y0: tuple[int, int], direction: Direction, dungeon: Dungeon) -> None:
        x0, y0 = x_y0
        # Using a dict ensures that entries are ordered by smallest distance first.
        self.visible_tiles = {}
        if self.shape == SightShape.TRUE:
            for tile in dungeon.visible_tiles_at(x0, y0):
                x, y, d = tile
                if d <= self.radius:
                    self.visible_tiles[(x, y)] = None
        else:
            for tile in dungeon.non_shadowed_tiles_at(x0, y0):
                x, y, d = tile
                if d <= self.radius:
                    if self.is_tile_visible(tile, direction, (x0, y0)):
                        self.visible_tiles[(x, y)] = None

        self.visited_tiles.update(self.visible_tiles)

    def is_tile_visible(self, tile: tuple[int, int, float], direction: Direction, x0_y0: tuple[int, int]) -> bool:
        x, y, _ = tile
        x0, y0 = x0_y0
        if self.shape == SightShape.CIRCLE:
            # print(f"Tile {x, y} is visible from {x0, y0} in direction {direction} with distance {d} and radius {self.radius}")
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
        # print(f"Tile {x, y} is not visible from {x0, y0} in direction {direction} with distance {d} and radius {self.radius}")

        return False