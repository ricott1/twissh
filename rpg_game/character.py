import random,os, math, time
import action, location, item, game_class, entity
from rpg_game.utils import log, mod, roll, random_name, random_stats
from rpg_game.constants import *
from rpg_game.characteristic import Characteristic


             
class Character(entity.Entity):
    def __init__(self, _direction="right", _stats=None, **kwargs):
        super().__init__(_layer=1, **kwargs)
        
        self.direction = _direction

        self.movement_speed = 1
        self.recoil = 0
        
        self.level = 1
        self.exp = 0
        
        self.inventory = location.Inventory(size=4)
        self.equipment = {"main_hand" : None, "off_hand": None, "helm": None, "body":None, "belt":None, "gloves":None, "ring_1":None, "ring_2":None, "boots":None }
        self.crafting = {}
        #base value is the bare character value, without objects
        if not _stats:
            _stats = random_stats()
        self.HP = Characteristic("hit points", "HP", _stats["HP"], _min = 0, _max=9999)
        
        self.CON = Characteristic("constitution", "CON", _stats["CON"])
        self.STR = Characteristic("strength", "STR", _stats["STR"])
        self.DEX = Characteristic("dexterity", "DEX", _stats["DEX"])
        self.CHA = Characteristic("charisma", "CHA", _stats["CHA"])
        self.INT = Characteristic("intelligence", "INT", _stats["INT"])
        self.WIS = Characteristic("wisdom", "WIS", _stats["WIS"])
        
        self.print_action = self._print_action = ""
        self.print_action_time = self._print_action_time = 0
        
        self.game_class = game_class.Warrior()
        self.actions = self.game_class.actions
        self.action_counters = {}
        for key, act in self.actions.items():
            setattr(self, key, lambda action=act, **kwargs: action.use(self, **kwargs))
            self.action_counters[key] = 0. 

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
    def marker(self):
        if self.is_dead:
            return u"☠"
        if self.action_counters["parry"] > 0:
            return "X"
        return {"up":"▲", "down":"▼", "left":"◀", "right":"▶"}[self.direction]
    
    @property
    def recoil(self):
        return self._recoil

    @recoil.setter
    def recoil(self, value):
        self._recoil = min(MAX_RECOIL, max(0, value))
     
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
        
    def on_update(self, DELTATIME):
        if self.is_dead:
            return

        if self.print_action_time > 0:
            self.print_action_time -= DELTATIME

        s = int(self.recoil)
        if self.recoil > 0:
            self.recoil -= RECOIL_MULTI * DELTATIME
            #redraw only if integer changed, hence nneed to display it  
            self.redraw = int(self.recoil) < s

        for key in self.actions:
            self.actions[key].on_update(DELTATIME)
            if self.action_counters[key] > 0:
                self.action_counters[key] -= COUNTER_MULTI * DELTATIME
                if self.action_counters[key] <= 0:
                    #self.actions[key].on_end()
                    self.action_counters[key] = 0
                    self.redraw = True

    def hit(self, dmg):
        self.HP._dmg += max(1, dmg - self.dmg_reduction)
        if self.is_dead:
            self.set_death()

    def set_death(self):
        self.redraw = True
        self.location.redraw = True
        self.print_action = f"{self.name} is dead"
      
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
        obj.location.unregister(obj)
        x, y, z = free
        obj.position = (x, y, z)
        obj.location = self.inventory
        
    def remove_inventory(self, obj):
        if obj.is_equipped:
            for _type in obj.type:
                if self.equipment[_type] == obj:
                    self.unequip(_type)
                    break
        obj.location.unregister(obj)
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
        
    def unequip(self, _type):
        if self.equipment[_type]:
            self.equipment[_type].on_unequip()
        self.equipment[_type] = None
            

class Villain(Character):
    @property
    def marker(self):
        if self.is_dead:
            return u"☠"
        if self.action_counters["parry"] > 0:
            return ("monster", "X")
        return ("monster", super().marker)
    

class Player(Character): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_sent_log = []
        self.chat_received_log = []

    def handle_input(self, _input):
        if _input == "w":
            self.move_up()
        elif _input == "s":
            self.move_down()
        elif _input == "a":
            self.move_left()
        elif _input == "d":
            self.move_right()
        elif _input == "p":
            self.pick_up()
        elif _input == "l":
            self.attack()
        elif _input == "o":
            self.parry()
        elif _input == "k":
            self.fire()


