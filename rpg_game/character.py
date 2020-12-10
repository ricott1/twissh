import random,os, math, time
import ability, race, job, strategy, mission, inventory, item
from rpg_game.utils import log, mod
   


class Characteristic(object):
    def __init__(self, name, short, value, _min=3, _max=25):
        self.name = name
        self.short = short
        self._value = value
        self.bonus = {}
        self._min = _min
        self._max = _max
        self._dmg = 0

    @property
    def mod(self):
        return mod(self.value)

    @property
    def max(self):
        bonus = sum([b for k, b in self.bonus.items()])
        v = self._value + bonus
        return max(self._min, min(self._max, v))

    @property
    def value(self):
        bonus = sum([b for k, b in self.bonus.items()])
        v = self._value + bonus - self._dmg
        return max(self._min, min(self._max, v))  
    @value.setter
    def value(self, value):
        v = int(round(value))
        self._value = max(self._min, min(self._max, v))
    
    
             
class Character(object):
    MAX_RECOIL = 100
    LONG_RECOIL = 75
    MED_RECOIL = 50
    SHORT_RECOIL = 25
    ACTION_TIME_DEFAULT = 5
    HP_DMG_MULTI = 0.2
    HP_DMG_NORM = 100.
    HB_DMG_MULTI = 0.2
    HB_DMG_NORM = 100.
    RECOIL_MULTI = 9. 
    RECOIL_NORM = 6.
    LVUP_MULTI = 1000

    def __init__(self, _id, data, location = None):
        self.id = _id
        self.name = data["name"]
        self.redraw = False
        self.layer = 1
        
        self.location = location
        if location:
            free = [(i, j) for j, line in enumerate(self.location.content) for i, l in enumerate(line)  if not l]
            x, y = random.choice(free)
            self.position = (x, y)
            self.location.register(self)
        else:
            self.position = (0, 0)
        self.direction = "right"

        _race = random.sample(race.get_player_races(), 1)[0]
        _job = random.sample(job.get_jobs(), 1)[0]
        
        self.description = []
        self.recoil = 0
        
        self.level = 1
        self.exp = 0
        
        self.bonus = {}
        self.immunities = {}
        self.inventory = []#data["inventory"]
        self.equipment = {}#data["equipment"] #key = type, value = object
        self.crafting = {}
        #base value is the bare character value, without objects
        self.HP = Characteristic("hit points", "HP", data["HP"], _min = 0, _max=9999)
        
        self.CON = Characteristic("constitution", "CON", data["CON"])
        self.STR = Characteristic("strength", "STR", data["STR"])
        self.DEX = Characteristic("dexterity", "DEX", data["DEX"])
        self.CHA = Characteristic("charisma", "CHA", data["CHA"])
        self.INT = Characteristic("intelligence", "INT", data["INT"])
        self.WIS = Characteristic("wisdom", "WIS", data["WIS"])

        self.characteristics = []
        
        self.acquiredTargets = []
        self.print_action = ""
        self.action_time = 0
        
        self.abilities = {"offense" : ability.Attack()}#, "defense" , "recover", "special",'support"
        #attributes that print the ongoing action
        
        self.restore()
    
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
    def AC(self):
        return 10 + self.DEX.mod
    
    @property
    def recoil(self):
        return self._recoil

    @recoil.setter
    def recoil(self, value):
        self._recoil = min(self.MAX_RECOIL, max(0, value))
              
    @property
    def is_dead(self):
        if self.hp <= 0:
            return True
        return False
        
    def on_update(self, DELTATIME):
        if self.is_dead:
            self.set_death()#should set redraw only if first time death
            return

        if self.action_time > 0:
            self.action_time -= DELTATIME
            if self.action_time <= 0:
                self.action_time = 0
                self.print_action = ""
                self.redraw = True

        s = int(self.recoil)
        if self.recoil > 0:
            self.recoil -= self.RECOIL_MULTI * DELTATIME * (1. + self.DEX.mod/self.RECOIL_NORM)
            #redraw only if integer changed, hence nneed to display it  
            self.redraw = self.redraw or int(self.recoil) < s
    
    def set_death(self):
        self.print_action = f"{self.name} is dead"
      
    def restore(self):
        self.HP._dmg = 0
        
    def add_experience(self, exp):
        self.exp += exp
        while self.exp>= self.level**2*1000:
            self.level_up()
          
    def level_up(self):
        self.restore()

    def move(self, direction):
        self.direction = direction
        x, y = self.position 
        new_x = x + int(self.direction=="right") - int(self.direction=="left")
        new_y = y + int(self.direction=="down") - int(self.direction=="up")
        if self.location.is_empty((new_x, new_y), self.layer):
            self.location.clear(self.position, self.layer)
            self.position = (new_x, new_y)
            self.location.register(self)
            
    def add_inventory(self, obj):
        self.inventory.append(obj)
        
    def remove_inventory(self, obj):
        self.unequip(obj)
        self.inventory.remove(obj)
            
    def equip(self, obj):
        if obj.type in self.equipment:
            self.equipment[obj.type].on_unequip(self)
        self.equipment[obj.type] = obj
        obj.on_equip(self)
        
    def unequip(self, obj):
        if obj.type in self.equipment and self.equipment[obj.type] == obj:
            self.equipment.pop(obj.type)
            obj.on_unequip(self)
    
    def pickup(self):
        x, y = self.position
        target = self.location.content[y][x][0]
        if isinstance(target, item.Item):
            self.location.clear(target.position, target.layer)
            self.add_inventory(target)
            target.location = self

            self.recoil += self.LONG_RECOIL
            self.print_action = "Picked up: {}".format(target.name)
            self.action_time = self.ACTION_TIME_DEFAULT
            

    def drop(self, item):
        x, y = self.position
        if self.location.is_empty((x, y), 0):
            item.position = (x, y)
            self.location.register(item)
            self.remove_inventory(item)
            item.location = self.location

            self.recoil += self.MED_RECOIL
            self.print_action = "Dropped: {}".format(item.name)
            self.action_time = self.ACTION_TIME_DEFAULT
        
           
class Villain(Character):
    @property
    def marker(self):
        if self.direction == "up":
            return "△"
        elif self.direction == "down":
            return "▽"
        elif self.direction == "left":
            return "◁"
        elif self.direction == "right":
            return "▷" 
    
    
class Player(Character):   
    @property
    def marker(self):
        if self.direction == "up":
            return "▲"
        elif self.direction == "down":
            return "▼"
        elif self.direction == "left":
            return "◀"
        elif self.direction == "right":
            return "▶"

