import random,os, math, time
import action, location, item, entity, strategy, game_class, counter
from rpg_game.utils import log, mod, roll, random_name, random_stats
from rpg_game.constants import *
from rpg_game.characteristic import Characteristic


             
class Character(entity.ActingEntity):
    def __init__(self, _direction="right", _stats=None, **kwargs):
        if not _stats:
            _stats = random_stats()
        super().__init__(_layer=1, _HP=_stats["HP"], **kwargs)
        self.direction_markers = {"up":["▲"], "down":["▼"], "left":["◀"], "right":["▶"]}

        self.level = 1
        self._exp = 0
        
        self.inventory = location.Inventory()
        self.equipment = {"main_hand" : None, "off_hand": None, "helm": None, "body":None, "belt":None, "gloves":None, "ring":None, "boots":None }
        self.crafting = {}
        #base value is the bare character value, without objects
        
        self.CON = Characteristic(self, "constitution", "CON", _stats["CON"])
        self.STR = Characteristic(self, "strength", "STR", _stats["STR"])
        self.DEX = Characteristic(self, "dexterity", "DEX", _stats["DEX"])
        self.CHA = Characteristic(self, "charisma", "CHA", _stats["CHA"])
        self.INT = Characteristic(self, "intelligence", "INT", _stats["INT"])
        self.WIS = Characteristic(self, "wisdom", "WIS", _stats["WIS"])

        self.movement_speed = BASE_MOVEMENT_SPEED
        

    @property
    def dmg_reduction(self):
        tot = 0
        for part, eqp in self.equipment.items():
            if eqp and hasattr(eqp, "dmg_reduction"):
                tot += eqp.dmg_reduction
        return tot

    @property
    def game_class(self):
        return self._game_class
    
    @game_class.setter
    def game_class(self, value):
        self._game_class = value
        self.actions = self.game_class.actions
        self.class_actions = self.game_class.class_actions
        for obj in self.game_class.initial_inventory:
            i = obj(self.location)
            free = self.inventory.free_position(i)
            if free:
                self.add_inventory(i, free)

    @property
    def invulnerable(self):
        return "charge" in self.counters

    @property
    def exp(self):
        return self._exp
    @exp.setter
    def exp(self, value):
        self._exp = value
        while self.exp>= (self.level**2)*EXP_PER_LEVEL:
            self.increase_level()
    
    @property
    def is_controllable(self):
        if "charge" in self.counters:
            return False
        if self.is_dead:
            return False
        return True

    @property
    def status(self):   
        if self.is_dead:
            h = u"X"
        elif self.HP.value < self.HP.max: 
            h = u"♡"
        elif self.HP.value == self.HP.max: 
            h = u"♥" 

        health_bars = int(round(self.HP.value/self.HP.max * HEALTH_BARS_LENGTH))
        recoil_bars = int(round((self.recoil)/MAX_RECOIL  * RECOIL_BARS_LENGTH))
        recoil = (RECOIL_BARS_LENGTH - recoil_bars) * "▰" + recoil_bars * u"▱" 
        
        if self.recoil == 0:
            recoil_type = "green"
        elif self.slow_recovery:
            recoil_type = "red"
        else:
            recoil_type = "yellow"

        action_text = ""
        if "text" in self.counters:
            action_text = self.counters["text"].text
        _status = [("name", f"{self.name:12s}"), (recoil_type, f"{recoil}"), ("top", f" {h}{self.HP.value:>3d}/{self.HP.max:<3d}"),  ("top", f" {action_text:<s}")]

        return _status

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        self.inventory.on_update(_deltatime)
        self.inventory.redraw = False

    def increase_level(self):
        for b in self.game_class.bonus:
            self.game_class.bonus[b] += 1
        self.movement_speed += 0.25
        self.HP._value += max(1, 2 + self.CON.mod)
        self.restore()

    def hit(self, dmg):
        if self.invulnerable:
            return
        dmg = max(1, dmg - self.dmg_reduction)
        self.HP.dmg += max(0, dmg)
        counter.ColorCounter(self, f"white", SHORT_RECOIL)
        self.location.redraw = True
    
    def kill(self):
        self.HP.dmg = self.HP.max

    def restore(self):
        self.HP.dmg = 0
            
    def add_inventory(self, obj, pos):
        obj.change_location(pos, self.inventory)
        
    def drop_inventory(self, obj, pos):
        if obj.is_equipment and obj.is_equipped:
            for _type in obj.type:
                if self.equipment[_type] == obj:
                    self.unequip(_type)
                    break
        obj.change_location(pos, self.location)
            
    def equip(self, obj):
        if not obj.is_equipment:
            return
        #if already equipped somwehere, then return
        if obj in [self.equipment[t] for t in self.equipment]:
            return
        
        for t in obj.type:
            self.unequip(t)
            self.equipment[t] = obj
            
        obj.on_equip()
        
    def unequip(self, _type):
        if self.equipment[_type]:
            if self.equipment[_type].type == "two_hands":
                self.equipment["main_hand"].on_unequip()
                self.equipment["off_hand"].on_unequip()
                self.equipment["main_hand"] = None
                self.equipment["off_hand"] = None
            else:
                self.equipment[_type].on_unequip()
                self.equipment[_type] = None
            

class Monster(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_class = game_class.Monster()
        self.strategy = strategy.MonsterStrategy(self, Player)
        self._color = "red"

    @property
    def status(self):
        if self.strategy.target:
            return super().status + [f" Target: {self.strategy.target.name}"]
        return super().status
        
    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        if self.is_controllable:
            action = self.strategy.action()
            if action:
                self.actions[action].use(self)
    

class Player(Character): 
    def __init__(self, _game_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = self.id
        self.game_class = getattr(globals()[f"game_class"], _game_class)()
        self.chat_sent_log = []
        self.chat_received_log = []
        self.input_map = {
            "up": "move_up",
            "down": "move_down",
            "left": "move_left",
            "right": "move_right",
            "shift up": "dash_up",
            "shift down": "dash_down",
            "shift left": "dash_left",
            "shift right": "dash_right",
            "q": "pick_up",
            "a": "attack"}

        extra_keys = ["s", "d", "w", "e"]
        for i, act in enumerate(self.class_actions):
            self.input_map[extra_keys[i]] = act

    def handle_input(self, _input):
        if _input in self.input_map and self.is_controllable:
            action = self.input_map[_input]
            if action in self.actions:
                self.actions[action].use(self)

