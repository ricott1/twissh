import random,os, math, time
import action, location, item, entity
from rpg_game.utils import log, mod, roll, random_name, random_stats
from rpg_game.constants import *
from rpg_game.characteristic import Characteristic
from rpg_game.game_class import *


             
class Character(entity.ActingEntity):
    def __init__(self, _direction="right", _stats=None, **kwargs):
        super().__init__(_layer=1, **kwargs)
        
        self.level = 1
        self.exp = 0
        
        self.inventory = location.Inventory(size=4)
        self.equipment = {"main_hand" : None, "off_hand": None, "helm": None, "body":None, "belt":None, "gloves":None, "ring_1":None, "ring_2":None, "boots":None }
        self.crafting = {}
        #base value is the bare character value, without objects
        if not _stats:
            _stats = random_stats()
        self.HP = Characteristic(self, "hit points", "HP", _stats["HP"], _min = 0, _max=9999)
        
        self.CON = Characteristic(self, "constitution", "CON", _stats["CON"])
        self.STR = Characteristic(self, "strength", "STR", _stats["STR"])
        self.DEX = Characteristic(self, "dexterity", "DEX", _stats["DEX"])
        self.CHA = Characteristic(self, "charisma", "CHA", _stats["CHA"])
        self.INT = Characteristic(self, "intelligence", "INT", _stats["INT"])
        self.WIS = Characteristic(self, "wisdom", "WIS", _stats["WIS"])
        
        self.print_action = self._print_action = ""
        self.print_action_time = self._print_action_time = 0
        self.action_marker = {}
        
        self.status_counters = {}
        self.movement_speed = 2.5

    @property
    def con(self):
        return self.CON.value
    @property
    def str(self):
        return self.STR.value
    @property
    def dex(self):
        return self.DEX.value
    @property
    def cha(self):
        return self.CHA.value
    @property
    def int(self):
        return self.INT.value
    @property
    def wis(self):
        return self.WIS.value
    @property
    def hp(self):
        return self.HP.value

    @property
    def atk(self):
        return self.STR.mod
    @property
    def ac(self):
        return 10 + self.DEX.mod
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
        for key, act in self.actions.items():
            if key not in self.action_counters:
                self.action_counters[key] = 0. 

    @property
    def marker(self):
        if self.is_dead:
            m = "X"
        elif self.action_marker:
            #m = {"up":"⨪", "down":"ꜙ", "left":"꜏", "right":"꜊"}[self.direction]
            m = self.action_marker[self.direction]
        else:
            m = {"up":"▲", "down":"▼", "left":"◀", "right":"▶"}[self.direction]
        return [m for _ in self.positions]
     
    @property
    def print_action(self):
        return self._print_action
     
    @print_action.setter
    def print_action(self, text):
        self.print_action_time = ACTION_TIME_DEFAULT
        self._print_action = text

    @property
    def print_action_time(self):
        return self._print_action_time
     
    @print_action_time.setter
    def print_action_time(self, value):
        self._print_action_time = value
        if self._print_action_time <= 0:
            self._print_action_time = 0
            self._print_action = ""
            self.redraw = True

    @property
    def is_dead(self):
        if self.hp <= 0:
            return True
        return False
        
    def on_update(self, _deltatime):
        self.redraw = False
        if self.is_dead:
            self.status_counters["dead"] -= COUNTER_MULTI * _deltatime
            if self.status_counters["dead"] <=0:
                self.destroy()
                return

        super().on_update(_deltatime)

        if self.print_action_time > 0:
            self.print_action_time -= _deltatime
        if self.action_marker:
            self.action_marker["time"] -= _deltatime
            if self.action_marker["time"] <=0:
                self.action_marker = {}

        for key in self.status_counters:
            if self.status_counters[key] > 0:
                self.status_counters[key] -= COUNTER_MULTI * _deltatime
                if self.status_counters[key] <= 0:
                    #self.actions[key].on_end()
                    self.status_counters[key] = 0

    def hit(self, dmg):
        self.HP._dmg += max(1, dmg - self.dmg_reduction)
        if self.is_dead:
            self.set_death()

    def set_death(self):
        self.redraw = True
        self.location.redraw = True
        self.print_action = f"{self.name} is dead"
        self.status_counters["dead"] = DEATH_INTERVAL
      
    def restore(self):
        self.HP._dmg = 0
        
    def add_experience(self, exp):
        self.exp += exp
        while self.exp>= self.level**2*1000:
            self.level_up()
          
    def level_up(self):
        self.restore()
            
    def add_inventory(self, obj):
        free = self.inventory.free_position(_layer=0)
        if not free:
            print("Inventory full")
            return
        # obj.location.unregister(obj)
        obj.position = free
        obj.location = self.inventory
        
    def remove_inventory(self, obj):
        if obj.is_equipped:
            for _type in obj.type:
                if self.equipment[_type] == obj:
                    self.unequip(_type)
                    break
        # obj.location.unregister(obj)
        x, y, z = self.position
        obj.position = (x, y, 0)
        obj.location = self.location
            
    def equip(self, obj, _type):
        if _type not in obj.type:
            return
        if not obj.is_equipment:
            return
        self.unequip(_type)
        self.equipment[_type] = obj
        obj.on_equip()
        print("EQUPP", self.STR.bonus, self.equipment[_type].bonus)
        
    def unequip(self, _type):
        if self.equipment[_type]:
            self.equipment[_type].on_unequip()
        self.equipment[_type] = None
            

class Villain(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_class = Monster()

    @property
    def marker(self):
        return [("monster", m) for m in super().marker]

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        if self.recoil == 0 and not self.is_dead and random.random() < 0.01:
            return
            {"up":action.MoveUp, "down":action.MoveDown, "left":action.MoveLeft, "right":action.MoveRight}[self.direction].use(self)
    

class Player(Character): 
    def __init__(self, _game_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.game_class = globals()[_game_class]()
        except:
            self.game_class = game_class.Monster()
        self.chat_sent_log = []
        self.chat_received_log = []
        self.input_map = {
            "w": "move_up",
            "s": "move_down",
            "a": "move_left",
            "d": "move_right",
            "W": "dash_up",
            "S": "dash_down",
            "A": "dash_left",
            "D": "dash_right",
            "p": "pick_up",
            "l": "attack"}

        extra_keys = ["o", "k", "j"]
        for i, act in enumerate(self.class_actions):
            self.input_map[extra_keys[i]] = act

    def handle_input(self, _input):
        if _input in self.input_map:
            action = self.input_map[_input]
            if action in self.actions:
                self.actions[action].use(self)
