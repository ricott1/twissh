from dataclasses import dataclass

from twissh.server import UrwidMind

from .base import Component


@dataclass
class User(Component):
    mind: None | UrwidMind
    last_input: str = ""
    color: tuple[int, int, int] = (255, 0, 0)
