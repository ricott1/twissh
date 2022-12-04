from __future__ import annotations
from enum import Enum


WIDTH = 80
HEIGHT = 24

NEXT_KEY = "space"
DEATH_INTERVAL = 3
COUNTER_MAX = 10

DASH_RECOIL_MULTI = 1.25
DASH_SPEED_MULTI = 2
BASE_MOVEMENT_SPEED = 1.75

ACTION_TIME_DEFAULT = 3
RECOIL_MULTI = COUNTER_MULTI = 1
LVUP_MULTI = 1000
GAME_SPEED = 1
REDRAW_MULTI = 10

SLOW_RECOVERY_MULTI = 0.5
MOD_WEIGHT = 0.1

EXP_PER_LEVEL = 1000
EXP_PER_KILL = 100

BASE_ATTACK_SPEED = 0.75

INVENTORY_SIZE = 12
MAX_NUM_QUICK_ITEMS = 5
EXTRA_ENCUMBRANCE_MULTI = 2


class Recoil(float, Enum):
    MINIMUM = 0.15
    SHORT = 0.25
    MEDIUM = 0.5
    LONG = 1

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

class KeyMap(str, Enum):
    INVENTORY_MENU = "I"
    STATUS_MENU = "S"
    HELP_MENU = "H"
    EQUIPMENT_MENU = "E"
    EXPLORER_MENU = "X"
    CHAT_MENU = "C"
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