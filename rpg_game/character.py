import random,os, math, time
import ability, race, job, strategy, mission, inventory, item
from rpg_game.utils import log, mod
   
             
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
    DREAM_MULTI = 0.25
    RTM_RANGE = 0.025
    LVUP_MULTI = 1000

    def __init__(self, _id, data, location = None):
        self.id = _id
        self.name = data["name"]
        self.redraw = False
        
        self.location = location
        if location:
            free = [(i, j) for j, line in enumerate(self.location.map_content) for i, l in enumerate(line)  if not l]
            x, y = random.choice(free)
            self.position = (x, y)
            self.location.map_content[y][x] = self
            self.location.has_changed = True
        else:
            self.position = (0, 0)
        self.direction = "right"

        _race = random.sample(race.get_player_races(), 1)[0]
        _job = random.sample(job.get_jobs(), 1)[0]
        self.job = _job
        self.race = _race
        self.mission = None
        
        self.description = []
        self.recoil = 10 + random.random() * 75
        
        self.level = 1
        self.exp = 0
        
        self.HB_damage = 0
        self.MP_damage = 0
        self.HP_damage = 0
        self.bonus = {"AC" : 0, "HP" : 0, "MP" : 0,  "HB" : 0, "RES" : 0, "STR" : 0, "DEX" : 0, "SPD" : 0, "MAG" : 0, "RTM" : 0}
        self.immunities = {"shock" : 0, "mute" : 0, "dream" :0, "death" : 0}
        self.inventory = []#data["inventory"]
        self.equipment = {}#data["equipment"] #key = type, value = object
        self.crafting = {}
        #base value is the bare character value, without objects
        self._MP, self.MP = data["MP"], data["MP"]
        self._HP, self.HP = data["HP"],data["HP"]

        self._STA, self.STA = data["HP"], data["MP"]
        self._HB, self.HB = data["HB"], data["HB"]
        
        self._RES, self.RES = data["RES"], data["RES"]
        self._STR, self.STR = data["STR"],data["STR"]
        
        self._DEX, self.DEX = data["DEX"],data["DEX"]
        self._SPD, self.SPD = data["SPD"],data["SPD"]
        
        self._MAG, self.MAG = data["MAG"],data["MAG"]
        self._RTM, self.RTM = data["RTM"],data["RTM"]
        
        self.acquiredTargets = []
        self.print_action = ""
        self.action_time = 0
             
        self.is_shocked = 0
        self.is_muted = 0
        self.is_dreaming = 0 
        
        self.on_rythm = 0
        
        self.abilities = {"offense" : ability.Attack()}#, "defense" , "recover", "special",'support"
        #attributes that print the ongoing action
        
        self.restore()
     
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
    

    @property
    def MP(self):
        bonus = sum([self.equipment[obj].bonus["MP"] for obj in self.equipment])
        return max(0, int(round(self._MP +  self.bonus["MP"] + self.race.bonus["MP"] + self.job.bonus["MP"] + bonus - self.MP_damage)))  
    @MP.setter
    def MP(self, value):
        self._MP = int(round(value))            
    
    @property
    def max_MP(self):
        return int(self.MP + self.MP_damage)
    
    
    @property
    def HP(self):
        bonus = sum([self.equipment[obj].bonus["HP"] for obj in self.equipment])
        return max(0, int(round(self._HP +  self.bonus["HP"] + self.race.bonus["HP"] + self.job.bonus["HP"] + bonus - self.HP_damage)))  
    @HP.setter
    def HP(self, value):
        self._HP = int(round(value))
        
    @property
    def max_HP(self):
        bonus = sum([self.equipment[obj].bonus["HP"] for obj in self.equipment])
        return max(0, int(round(self._HP +  self.bonus["HP"] + self.race.bonus["HP"] + self.job.bonus["HP"] + bonus)))  
        
        
    @property
    def STA(self):
        return min(self.HP, max(0, self._STA))
    @STA.setter
    def STA(self, value):
        self._STA = min(self.HP, max(0, value))  
            
    @property
    def HB(self):
        bonus = sum([self.equipment[obj].bonus["HB"] for obj in self.equipment])
        return max(0, int(self._HB + self.bonus["HB"]  + self.race.bonus["HB"] + self.job.bonus["HB"] + bonus + self.HB_damage))
    @HB.setter
    def HB(self, value):
        self._HB = max(0, int(round(value)))
        
    @property
    def max_HB(self):
        bonus = sum([self.equipment[obj].bonus["HB"] for obj in self.equipment])
        return max(0, int(self._HB + self.bonus["HB"]  + self.race.bonus["HB"] + self.job.bonus["HB"] + bonus))
        
                  
    @property
    def STR(self):
        bonus = sum([self.equipment[obj].bonus["STR"] for obj in self.equipment])
        return max(1, int(self._STR + self.bonus["STR"] + self.race.bonus["STR"] + self.job.bonus["STR"] + bonus))
    @STR.setter
    def STR(self, value):
        self._STR = max(0, int(round(value)))
    
               
    @property
    def SPD(self):
        bonus = sum([self.equipment[obj].bonus["SPD"] for obj in self.equipment])
        return max(1, int(self._SPD + self.bonus["SPD"] + self.race.bonus["SPD"] + self.job.bonus["SPD"] + bonus))
    @SPD.setter
    def SPD(self, value):
        self._SPD = max(0, int(round(value)))
                  
    @property
    def DEX(self):
        bonus = sum([self.equipment[obj].bonus["DEX"] for obj in self.equipment])
        return max(1, int(self._DEX + self.bonus["DEX"] + self.race.bonus["DEX"] + self.job.bonus["DEX"] + bonus))
    @DEX.setter
    def DEX(self, value):
        self._DEX = max(0, int(round(value)))
                  
    @property
    def MAG(self):
        bonus = sum([self.equipment[obj].bonus["MAG"] for obj in self.equipment])
        if self.is_muted:
            return  max(1, int(bonus))
        else:        
            return max(1, int(self._MAG + self.bonus["MAG"] + self.race.bonus["MAG"] + self.job.bonus["MAG"] + bonus))
    @MAG.setter
    def MAG(self, value):
        self._MAG = max(0, int(round(value)))
               
    @property
    def RES(self):
        bonus = sum([self.equipment[obj].bonus["RES"] for obj in self.equipment])
        if self.is_shocked:
            return  max(1, int(bonus))
        else:        
            return max(1, int(self._RES + self.bonus["RES"] + self.race.bonus["RES"] + self.job.bonus["RES"] + bonus))
    @RES.setter
    def RES(self, value):
        self._RES = max(0, int(round(value)))
           
    @property
    def RTM(self):
        bonus = sum([self.equipment[obj].bonus["RTM"] for obj in self.equipment]) + self.race.bonus["RTM"] + self.job.bonus["RTM"]
        return max(1, int(self._RTM + self.bonus["RTM"] + bonus))
    @RTM.setter
    def RTM(self, value):
        self._RTM = max(0, int(round(value)))
    
    @property
    def AC(self):
        return 10 + mod(self.DEX)
    
    @property
    def recoil(self):
        return self._recoil

    @recoil.setter
    def recoil(self, value):
        self._recoil = min(self.MAX_RECOIL, max(0, value))
    
      
    @property
    def is_shocked(self):
        return self._is_shocked
    @is_shocked.setter
    def is_shocked(self, value):
        immunities = self.all_immunities()
        if value > 0:
            if immunities["shock"]:
                self._is_shocked = 0
            else:
                self._is_shocked = value
        else:
            self._is_shocked = 0
        
    @property
    def is_muted(self):
        return self._is_muted
    @is_muted.setter
    def is_muted(self, value):
        immunities = self.all_immunities()
        if value > 0:
            if immunities["mute"]:
                self._is_muted = 0
            else:
                self._is_muted = value
        else:
            self._is_muted = 0
  
    @property
    def is_dreaming(self):
        return self._is_dreaming
    @is_dreaming.setter
    def is_dreaming(self, value):
        immunities = self.all_immunities()
        if value > 0:
            if immunities["dream"]:
                self._is_dreaming = 0
            else:
                self._is_dreaming = value
        else:
            self._is_dreaming = 0   
              
    @property
    def is_dead(self):
        if self.HP <= 0 or self.max_MP <= 0 or self.HB <= 0:
            self.set_death()
            return True
        return False

    def all_abilities(self):
        allAb = self.abilities.copy()
        
        obj_abilities = {}
        for obj in self.equipment:
            obj_abilities.update(self.equipment[obj].abilities)
        for (typ, ability) in obj_abilities.items():
            if typ in allAb:
                if ability.level > allAb[typ].level:
                    allAb[typ] = ability
            else:
                allAb[typ] = ability 
        for (typ, ability) in self.race.abilities.items():
            if typ in allAb:
                if ability.level > allAb[typ].level:
                    allAb[typ] = ability
            else:
                allAb[typ] = ability
        for (typ, ability) in self.job.abilities.items():
            if typ in allAb:
                if ability.level > allAb[typ].level:
                    allAb[typ] = ability
            else:
                allAb[typ] = ability
        
        return allAb
        
    def all_immunities(self):
    #when checking immunities should check all_immunities. fix this with update dictionaries
        allImm = self.immunities.copy()
        obj_immunities = {}
        for obj in self.equipment:
            obj_immunities.update(self.equipment[obj].immunities)
        allImm.update(obj_immunities)
        allImm.update(self.job.immunities)
        allImm.update(self.race.immunities)
        return allImm
        
    def update(self, DELTATIME):
        if self.is_dead:
            return

        if self.action_time > 0:
            self.action_time -= DELTATIME
            if self.action_time <= 0:
                self.action_time = 0
                self.print_action = ""
                self.redraw = True

        if self.recoil > 0:
            self.recoil -= self.RECOIL_MULTI * DELTATIME * (1. + mod(self.SPD)/self.RECOIL_NORM)
        
        s = int(self.STA)
        if self.STA < self.HP:
            self.STA += DELTATIME  
            #redraw only if integer changed, hence nneed to display it  
            self.redraw = self.redraw or int(self.STA) > s
    
    def set_death(self):
        self.MP = 0
        self.HP = 0
        self.HB = 0
        self.print_action = f"{self.name} is dead"
      
    def restore(self):
        self.HB_damage = 0
        self.MP_damage = 0
        self.HP_damage = 0
        for k in self.bonus:
            self.bonus[k] = max(self.bonus[k], 0)
        
        self.is_shocked = 0
        self.is_muted = 0
        
    def add_experience(self, exp):
        self.exp += exp
        while self.exp>= self.level**2*1000:
            self.level_up()
          
    def level_up(self):
        self.job.level_up()
        self.level = self.job.level
        self.restore()
    
    def target(self):
        x, y = self.position

        if self.direction == "up":
            position = (x, y-1)
        elif self.direction == "down":
            position = (x, y+1)
        elif self.direction == "left":
            position = (x-1, y)
        elif self.direction == "right":
            position = (x+1, y)

        return self.location.map_content[position[1]][position[0]]

    def move(self, direction):
        self.redraw = True
        self.direction = direction
        if not (self.is_dead or self.is_dreaming):
            self.location.has_changed = True
            target = self.target()
            if not target:
                x, y = self.position 
                new_x = x + int(self.direction=="right") - int(self.direction=="left")
                new_y = y + int(self.direction=="down") - int(self.direction=="up")
                self.location.map_content[y][x] = None
                self.location.map_content[new_y][new_x] = self
                self.position = (new_x, new_y)
            
    def add_inventory(self, obj):
        obj.location = self
        self.inventory.append(obj)
        self.location.has_changed = True
        
    def remove_inventory(self, obj):
        obj.location = self.location
        obj.location.inventory.append(obj)
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
        target = self.target()
        if isinstance(target, item.Item):
            self.recoil += self.LONG_RECOIL
            self.add_inventory(target)
            self.print_action = "Picked up: {}".format(target.name)
            self.action_time = self.ACTION_TIME_DEFAULT  
            self.redraw = True     

    def drop(self, item):
        self.recoil += 5
        self.remove_inventory(item)
        self.print_action = "Dropped: {}".format(item.name)
        self.action_time = self.ACTION_TIME_DEFAULT
         
    def craft(self, item):
        self.recoil = self.MAX_RECOIL
        self.add_inventory(item)
        for i in self.craft[item]:
            self.remove_inventory(i)
        self.print_action = "Crafted: {}".format(item.name)
        self.action_time = self.ACTION_TIME_DEFAULT 
        
           
class Villain(Character):
    pass
    
    
class Player(Character):   
    def start_mission(self, mission):
        self.mission = mission  
        mission.on_start() 

