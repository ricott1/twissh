from dataclasses import dataclass

from hacknslassh.components.description import GameClassName
from .base import Component


@dataclass
class TransformedToken(Component):
    into: GameClassName

@dataclass
class IncreasedSightToken(Component):
    values: list[int]
