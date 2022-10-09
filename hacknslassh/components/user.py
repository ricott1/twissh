# from __future__ import annotations
from dataclasses import dataclass
from .base import Component


@dataclass
class User(Component):
    mind: None
    last_input: str = ""
    # visible_map: list[list[str]] = [""]



