UPDATE_TIMESTEP = 0.035


MAX_RECOIL = 5
LONG_RECOIL = 2
MED_RECOIL = 1
SHORT_RECOIL = 0.5
SHORTER_RECOIL = 0.25
MIN_RECOIL = 0.1
DEATH_INTERVAL = 3
COUNTER_MAX = 10

DASH_RECOIL_MULTI = 1.25
DASH_SPEED_MULTI = 2
BASE_MOVEMENT_SPEED = 1.25

ACTION_TIME_DEFAULT = 3
RECOIL_MULTI = COUNTER_MULTI = 1 
LVUP_MULTI = 1000
GAME_SPEED = 1
REDRAW_MULTI = 10
DIRECTIONS = ("up", "down", "left", "right")
SLOW_RECOVERY_MULTI = 0.5
MOD_WEIGHT = 0.1

EXP_PER_LEVEL = 1000
EXP_PER_KILL = 100


HEALTH_BARS_LENGTH = RECOIL_BARS_LENGTH = 15

INVENTORY_SIZE = 12
EXTRA_ENCUMBRANCE_MULTI = 2




###DEFAULT KEY MAP
KEY_MAP = {
	"inventory-menu" : "ctrl a", 
	"status-menu" : "ctrl s",
	"help-menu" : "ctrl d",
	"equipment-menu" : "ctrl e",

	"up": "move_up",
    "down": "move_down",
    "left": "move_left",
    "right": "move_right",
    "shift up": "dash_up",
    "shift down": "dash_down",
    "shift left": "dash_left",
    "shift right": "dash_right",
    "q": "pick_up",
    "a": "attack",
    "s": "class_ability_1",
    "d": "class_ability_2",
    "w": "class_ability_3",
    "e": "class_ability_4",
}