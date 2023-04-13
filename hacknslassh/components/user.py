from dataclasses import dataclass
from hacknslassh.color_utils import Color
from web.server import UrwidMind
from .base import Component


@dataclass
class User(Component):
    mind: None | UrwidMind
    last_input: str = ""
    color: tuple[int, int, int] = Color.RED
