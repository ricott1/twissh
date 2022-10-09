from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any
from .base import Component

class Direction(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class Markers(object):
    USER = {
        Direction.UP: "▲",
        Direction.DOWN: "▼",
        Direction.LEFT: "◀",
        Direction.RIGHT: "▶",
    }
    WALL = "#"
    DOUBLE = {
        Direction.UP: "◢◣",
        Direction.DOWN: "◥◤",
        Direction.LEFT: "◀",
        Direction.RIGHT: "▶",
    }

@dataclass
class InLocation(Component):
    """
    Component for entities that are in a location.
    """
    # from ..location import Location
    location: Any
    position: tuple[int, int, int] = (0, 0, 0)
    direction: Direction = Direction.UP
    marker: str = Markers.USER[Direction.UP]
    fg: tuple[int, int, int] = (255, 255, 255)
    bg: tuple[int, int, int] | None = None
    visibility: int = 255

    @property
    def forward(self) -> tuple[int, int, int]:
        delta_x = int(self.direction == Direction.DOWN) - int(self.direction == Direction.UP)
        delta_y = int(self.direction == Direction.RIGHT) - int(self.direction == Direction.LEFT)
        x, y, z = self.position
        return (x + delta_x, y + delta_y, z)

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