from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass

import esper

from hacknslassh.color_utils import Color, closest_c256
if TYPE_CHECKING:
    from hacknslassh.components import ActorInfo

from .base import Component


@dataclass
class TransformedToken(Component):
    _from: ActorInfo
    _into: ActorInfo
    extra_components: dict[str, Component]
    on_processor: Callable[[esper.World, int, float], None] | None

@dataclass
class IncreasedSightToken(Component):
    values: list[int]
    on_processor: Callable[[esper.World, int, float], None] | None = None

@dataclass
class CatchableToken(Component):
    owner: int | None = None

@dataclass
class ColorDescriptor(Component):
    colors: tuple[Color, Color, Color, Color]

    def __post_init__(self):
        self.colors = [closest_c256(color) for color in self.colors]

    def to_bytes(self) -> bytes:
        return b"".join([x.to_bytes(1) for color in self.colors for x in color])

    @classmethod
    def from_bytes(cls, data: bytes) -> ColorDescriptor:
        return ColorDescriptor(tuple(tuple(data[i:i+3]) for i in range(0, len(data), 3)))
    
    @classmethod
    def from_hex(cls, data: str) -> ColorDescriptor:
        _colors = tuple(tuple(int(data[i + j:i + j + 2], 16) for i in (0, 2, 4)) for j in range(0, len(data), 6))
        return ColorDescriptor(_colors)
    
    def hex(self) -> str:
        c = self.colors
        def color_hex(color: Color) -> str:
            return f"{hex(color[0])[2:].zfill(2)}{hex(color[1])[2:].zfill(2)}{hex(color[2])[2:].zfill(2)}"
        return f"{color_hex(c[0])}{color_hex(c[1])}{color_hex(c[2])}{color_hex(c[3])}"
    
@dataclass
class BodyPartsDescriptor(Component):
    parts: tuple[int, int, int, int, int, int]

    def to_bytes(self) -> bytes:
        return b"".join([p.to_bytes(1) for p in self.parts])

    @classmethod
    def from_bytes(cls, data: bytes) -> BodyPartsDescriptor:
        return BodyPartsDescriptor(tuple([d for d in data]))
    
    @classmethod
    def from_hex(cls, data: str) -> BodyPartsDescriptor:
        return BodyPartsDescriptor(tuple([int(data[i:i+2], 16) for i in range(0, len(data), 2)]))

    def hex(self) -> str:
        return "".join([hex(p)[2:].zfill(2) for p in self.parts])