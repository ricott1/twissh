from __future__ import annotations
from enum import Enum
import random


WIDTH = 80
HEIGHT = 24

GAME_SPEED = 1

NEXT_KEY = "space"
DEATH_INTERVAL = 3
COUNTER_MAX = 10

MAX_NUM_QUICK_ITEMS = 5
MIN_ALPHA = 55


class Color(tuple[int, int, int], Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    DARK_RED = (128, 0, 0)
    DARK_GREEN = (0, 128, 0)
    DARK_BLUE = (0, 0, 128)
    DARK_YELLOW = (128, 128, 0)
    DARK_CYAN = (0, 128, 128)
    ORANGE = (255, 128, 0)
    BROWN = (128, 64, 0)
    PINK = (255, 0, 128)
    PURPLE = (128, 0, 255)
    TURQUOISE = (0, 128, 255)
    VIOLET = (128, 0, 255)
    SALMON = (255, 128, 128)
    SEA_GREEN = (0, 255, 128)
    SLATE_BLUE = (0, 128, 255)
    SLATE_GRAY = (0, 128, 128)
    TAN = (255, 128, 64)
    TOMATO = (255, 128, 64)
    WHEAT = (255, 255, 128)
    YELLOW_GREEN = (128, 255, 0)
    KHAKI = (192, 192, 64)
    ORCHID = (128, 0, 128)

    @classmethod
    def random(cls) -> Color:
        return random.choice(list(cls))



class Recoil(float, Enum):
    MINIMUM = 0.15
    SHORT = 0.25
    MEDIUM = 0.5
    LONG = 1
    MAX = 2

class MapSize(object):
    SMALL = (20, 20)
    MEDIUM = (40, 20)
    LARGE = (80, 20)

###DEFAULT KEY MAP

class ChatKeyMap(str, Enum):
    SEND = "enter"
    DELETE = "backspace"
    CLEAR = "ctrl k"
    CARRIAGE_RETURN = "ctrl a"

class ExplorerKeyMap(str, Enum):
    NEXT = "l"
    PREVIOUS = "k"

class KeyMap(str, Enum):
    INVENTORY_MENU = "I"
    STATUS_MENU = "S"
    HELP_MENU = "H"
    EQUIPMENT_MENU = "E"
    EXPLORER_MENU = "X"
    CHAT_MENU = "C"
    MINIMAP_MENU = "M"
    QUICK_MENU = "Q"
    TOGGLE_FULL_MENU = "tab"
    CENTER_CAMERA = "c"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"



MenuKeyMap = [KeyMap.STATUS_MENU, KeyMap.INVENTORY_MENU, KeyMap.EQUIPMENT_MENU, KeyMap.HELP_MENU, KeyMap.CHAT_MENU]

class Tile:
    EMPTY = " "
    WALL = "█"
    FLOOR = "."
    STAIRS_UP = "<"
    STAIRS_DOWN = ">"