from dataclasses import dataclass
from typing import Callable

from hacknslassh.components.base import Component
from hacknslassh.constants import Recoil


@dataclass
class DelayCallback(Component):
    """
    Component for delaying a callback.
    """

    callback: Callable
    delay: float


@dataclass
class DeathCallback(Component):
    """
    Component for delaying a callback.
    """

    delay = 5
