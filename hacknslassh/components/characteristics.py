from __future__ import annotations

from dataclasses import dataclass
import random

from ..utils import roll3d6
from .base import Component

@dataclass
class RGB(Component):
    red: ColorCharacteristic
    green: ColorCharacteristic
    blue: ColorCharacteristic

    @property
    def strength(self) -> int:
        return 3 + self.red.value//15
    
    @property
    def dexterity(self) -> int:
        return 3 + self.green.value//15
    
    @property
    def acumen(self) -> int:
        return 3 + self.blue.value//15
    
    @property
    def alpha(self) -> int:
        return max(self.red.value, self.green.value, self.blue.value)

    @classmethod
    def random(cls) -> RGB:
        return RGB(ColorCharacteristic(random.randint(0, 255)), ColorCharacteristic(random.randint(0, 255)), ColorCharacteristic(random.randint(0, 255)))

    @classmethod
    def human(cls) -> RGB:
        return RGB(ColorCharacteristic(255, 255), ColorCharacteristic(255, 255), ColorCharacteristic(255, 255))

    @classmethod
    def elf(cls) -> RGB:
        return RGB(ColorCharacteristic(185, 185), ColorCharacteristic(215, 215), ColorCharacteristic(255, 255))

    @classmethod
    def cat(cls) -> RGB:
        return RGB(ColorCharacteristic(155, 155), ColorCharacteristic(255, 255), ColorCharacteristic(155, 155))
    
    @classmethod
    def devil(cls) -> RGB:
        return RGB(ColorCharacteristic(255, 255), ColorCharacteristic(0, 0), ColorCharacteristic(0, 0))

    @classmethod
    def orc(cls) -> RGB:
        return RGB(ColorCharacteristic(215, 215), ColorCharacteristic(255, 255), ColorCharacteristic(155, 155))
    
    @classmethod
    def dwarf(cls) -> RGB:
        return RGB(ColorCharacteristic(255, 255), ColorCharacteristic(155, 155), ColorCharacteristic(215, 215))


    
    def kill(self) -> None:
        self.red.value = 0
        self.green.value = 0
        self.blue.value = 0

class ColorCharacteristic(Component):
    def __init__(self, value: int, max_value: int = 255) -> None:
        self._value = value
        self.max_value = max_value

    @property
    def value(self) -> int:
        return min(self.max_value, max(0, int(self._value)))
    
    @value.setter
    def value(self, _value: float) -> None:
        self._value = min(self.max_value, max(0, _value))


@dataclass
class RedRegeneration(Component):
    """
    Component for red regeneration.
    """

    value: int = 1
    frames_to_regenerate: int = 10
    frame: int = 0

@dataclass
class BlueRegeneration(Component):
    """
    Component for blue regeneration.
    """

    value: int = 1
    frames_to_regenerate: int = 10
    frame: int = 0

@dataclass
class GreenRegeneration(Component):
    """
    Component for green regeneration.
    """

    value: int = 1
    frames_to_regenerate: int = 10
    frame: int = 0