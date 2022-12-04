from __future__ import annotations
from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass

import esper
if TYPE_CHECKING:
    from hacknslassh.components import Info

from .base import Component


@dataclass
class TransformedToken(Component):
    _from: Info
    _into: Info
    extra_components: dict[str, Component]
    on_processor: Callable[[esper.World, int, float], None] | None

@dataclass
class IncreasedSightToken(Component):
    values: list[int]
    on_processor: Callable[[esper.World, int, float], None] | None = None
