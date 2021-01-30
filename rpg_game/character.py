import os, math, time
import action, location, item, entity, strategy, game_class, counter
from rpg_game.utils import log, mod, roll, random_name, random_stats, roll1d20, roll1d4
from rpg_game.constants import *
from rpg_game.characteristic import Characteristic


             
class Character(entity.ActingEntity):
    def __init__(self, _game_class, _direction="right", _stats=None, **kwargs):
        _game_class = getattr(globals()[f"game_class"], _game_class)
        if not _stats:
            _stats = random_stats(_game_class.stats_level)
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

        self._MP = Characteristic(self, "monster points", "MP", 0, _min = 0, _max=9999)
        self._game_class = None
        self.game_class = _game_class()

    
    @property
    def equipment_set(self):
        return set(eqp for part, eqp in self.equipment.items() if eqp)
    
    @property
    def dmg_reduction(self):
        _bonus = sum([self.full_eqp_bonus(eqp, "dmg_reduction") for eqp in self.equipment_set])
        if "dmg_reduction" in self.game_class.bonus:
            _bonus += self.game_class.bonus["dmg_reduction"]
        return _bonus

    @property
    def movement_speed(self):
        _bonus = sum([self.full_eqp_bonus(eqp, "movement_speed") for eqp in self.equipment_set])
        if "movement_speed" in self.game_class.bonus:
            _bonus += self.game_class.bonus["movement_speed"]
        return self._movement_speed + _bonus

    @property
    def encumbrance(self):
        _bonus = sum([self.full_eqp_bonus(eqp, "encumbrance") for eqp in self.equipment_set])
        if "encumbrance" in self.game_class.bonus:
            _bonus += self.game_class.bonus["encumbrance"]
        return self.STR.value + _bonus

    @property
    def game_class(self):
        return self._game_class
    
    @game_class.setter
    def game_class(self, value):
        if not self._game_class:
            get_inventory = True
        else:
            get_inventory = False
        self._game_class = value
        self.actions = self.game_class.actions
        self.class_actions = self.game_class.class_actions
        if get_inventory:
            for obj in self.game_class.initial_inventory:
                i = obj(self.location)
                self.add_inventory(i)
        
    
    @property
    def MP(self):
        return self._MP.value
    @MP.setter
    def MP(self, value):
        value = min(20, value)
        self._MP._value = value
        if roll1d20() < self.MP:
            self.transform()

    @property
    def invulnerable(self):
        return "charge" in self.counters

    @property
    def slow_recovery(self):
        if self.encumbrance < self.inventory.encumbrance:
            return True
        return self._slow_recovery
    @slow_recovery.setter
    def slow_recovery(self, value):
        self._slow_recovery = value
    

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
        _status = [("name", f"{self.name:12s}"), (recoil_type, f"{recoil}"), (self.color, f" {h}"), ("top", f"{self.HP.value:>3d}/{self.HP.max:<3d}"),  ("top", f" {action_text:<s}")]

        return _status

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        self.inventory.on_update(_deltatime)
        self.inventory.redraw = False

    def transform(self):
        self._color = "red"
        self.game_class = game_class.Monster()

    def full_eqp_bonus(self, eqp, key):
        _bonus = 0
        if key in eqp.bonus:
            _bonus += eqp.bonus[key]
        if eqp.rarity == "set" and key in eqp.set_bonus:
            set_name = eqp.set["name"]
            size = eqp.set["size"]
            if sum([1 if e.set["name"]==set_name else 0 for e in self.equipment_set ]) == size:
                _bonus += eqp.set_bonus[key]
        return _bonus

    def increase_level(self):
        for cts, lev in self.game_class.stats_level.items():
            if roll1d4() <= lev:
                self.game_class.bonus[cts] += 1
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

    def use_quick_item(self, obj):
        if obj and obj.is_equipment and not obj.is_equipped:
            self.actions["equip"].use(self, obj)
        elif obj and obj.is_equipment and obj.is_equipped:
            self.actions["unequip"].use(self, obj)
        elif obj and obj.is_consumable:
            self.actions["consume"].use(self, obj)
            
    def add_inventory(self, obj):
        if self.inventory.has_free_spot() and EXTRA_ENCUMBRANCE_MULTI*self.encumbrance >= self.inventory.encumbrance + obj.encumbrance:
            self.inventory.add(obj)
            
    def drop_inventory(self, obj):
        free = self.location.is_empty(self.floor)
        if free:
            if obj.is_equipment and obj.is_equipped:
                if obj.type == "two_hands":
                    self.unequip(self.equipment["main_hand"])
                    self.unequip(self.equipment["off_hand"])
                else:
                    self.unequip(self.equipment[obj.type])
            obj.change_location(self.floor, self.location)
            
    def equip(self, obj):
        if not obj.is_equipment:
            return
        #if already equipped somwehere, then return
        if obj in [self.equipment[t] for t in self.equipment]:
            return
        
        if obj.type == "two_hands":
            self.unequip(self.equipment["main_hand"])
            self.unequip(self.equipment["off_hand"])
            self.equipment["main_hand"] = obj
            self.equipment["off_hand"] = obj
        else:
            self.unequip(self.equipment[obj.type])
            self.equipment[obj.type] = obj
            
        obj.on_equip()
        
    def unequip(self, obj):
        if not obj or not obj.is_equipped:
            return
        if obj.type == "two_hands":
            self.equipment["main_hand"] = None
            self.equipment["off_hand"] = None
        else:
            self.equipment[obj.type] = None
        obj.on_unequip()
            

class Monster(Character):
    def __init__(self, **kwargs):
        super().__init__("Monster", **kwargs)
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
        super().__init__(_game_class, *args, **kwargs)
        self._color = self.id

    def handle_input(self, _input):
        if not self.is_controllable:
            return
        if _input in self.actions:
            self.actions[_input].use(self)
        elif _input in self.game_class.class_input:
            _action = self.game_class.class_input[_input]
            self.class_actions[_action].use(self)

