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

class Recoil(float, Enum):
    ZERO = 0
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
    TOGGLE_WRITE = "ctrl w"

class KeyMap(str, Enum):
    INVENTORY_MENU = "I"
    STATUS_MENU = "S"
    HELP_MENU = "H"
    EQUIPMENT_MENU = "E"
    EXPLORER_MENU = "X"
    CHAT_MENU = "C"
    LOG_MENU = "L"
    # EXIT_CHAT_MENU = "esc"
    MINIMAP_MENU = "M"
    QUICK_MENU = "Q"
    TOGGLE_FULL_MENU = "tab"
    CENTER_CAMERA = "c"
    CHANGE_RESOLUTION = "r"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    PICK_UP = "p"
    CATCH = "c"
    DROP_1 = "!"
    DROP_2 = "@"
    DROP_3 = "#"
    DROP_4 = "$"
    DROP_5 = "%"
    USE_1 = "1"
    USE_2 = "2"
    USE_3 = "3"
    USE_4 = "4"
    USE_5 = "5"
    TARGET_NEXT = "l"
    TARGET_PREVIOUS = "k"
    TARGET_SELF = "s"
    TOGGLE_AUTO_TARGET = "j"
    DIG = "d"
    TRANSFORM = "t"

MenuKeyMap = [KeyMap.STATUS_MENU, KeyMap.INVENTORY_MENU, KeyMap.EQUIPMENT_MENU, KeyMap.HELP_MENU, KeyMap.CHAT_MENU]

class Tile:
    EMPTY = " "
    WALL = "█"
    FLOOR = "."
    STAIRS_UP = "<"
    STAIRS_DOWN = ">"