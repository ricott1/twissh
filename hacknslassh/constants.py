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
    EXIT_CHAT_MENU = "esc"
    MINIMAP_MENU = "M"
    QUICK_MENU = "Q"
    TOGGLE_FULL_MENU = "tab"
    CENTER_CAMERA = "c"
    CHANGE_RESOLUTION = "r"
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