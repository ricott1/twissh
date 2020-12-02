import strategy, ability
class Job(object):
    def __init__(self, name='', description='', inventory=[], abilities={}, strategy = {},
                immunities={}, bonus={'MP' : 0, 'HP' : 0, 'HB' : 0, 'RES' : 0, 'STR' : 0, 'DEX' : 0, 'SPD' : 0, 'MAG' : 0, 'RTM' : 0, "AC" : 0}):
        self.name = name
        self.strategy = strategy
        self.description = description
        self.inventory = inventory
        self.abilities = abilities
        self.immunities = immunities
        self.bonus = bonus
        
        self.level=1
        self.proficiency = int(self.level/4)
        
    def level_up(self):
        self.level += 1
        self.bonus.update(self.level_bonus[self.level])
    def on_update(self, *args):
        pass   
        
class Student(Job):
    def __init__(self):
        super(Student, self).__init__(name = "Student", description = "A poor student", abilities = {"support" :  ability.Push()}, strategy = strategy.Student())
        #self.inventory.append("Pen")
        
        self.level_bonus = {lev : {"MP" : 2 + lev, "HP" : 2* (lev-1), "HB" : 0, "RES" : int(lev/4), "STR" : 0, "DEX" : 0, "SPD" : int(lev/3), "MAG" : 1+int(lev/2), "RTM" : int(lev/4)} for lev in range(1, 21)}                   
                            
        self.bonus.update(self.level_bonus[1])
        
        
class Wanderer(Job):
    def __init__(self):
        super(Wanderer, self).__init__(name = "Wanderer", description = "A poor Wanderer", abilities = {"support" :  ability.Dash()}, strategy = strategy.Wanderer())
        self.level_bonus = {lev : {"MP" : int(lev/2), "HP" : 3* (lev-1), "HB" : lev, "RES" : 1 + int(lev/2), "STR" : int(lev/2), "DEX" : 0, "SPD" : int(lev/3), "MAG" : 0, "RTM" : int(lev/6)} for lev in range(1, 21)}                    
                            
        self.bonus = self.level_bonus[1]
    def on_update(self, DELTATIME, player):
        self.bonus["AC"]  = max(0, player.MAGmod) 
        
class Protector(Job):
    def __init__(self):
        super(Protector, self).__init__(name = "Protector", description = "The pure Protector", abilities = {"support" :  ability.Dash(), "job special" :  ability.Confuse()}, strategy = strategy.Protector())                  
        self.level_bonus = {lev : {"MP" : 1 + int(lev/3), "HP" : 3* (lev-1), "HB" : 1 + int(lev/2), "RES" : int(lev/2), "STR" : 1 + int(lev/2), "DEX" : 0, "SPD" : int(lev/3), "MAG" : int(lev/3), "RTM" : int(lev/6)} for lev in range(1, 21)}                   
        self.bonus.update(self.level_bonus[1])
        
        
class Barbarian(Job):
    def __init__(self):
        super(Barbarian, self).__init__(name = "Barbarian", description = "The wild Barbarian", abilities = {"job special" :  ability.Frenzy()}, strategy = strategy.Barbarian())
       
                            
        self.level_bonus = {lev : {"MP" : 0, "HP" : 4* (lev-1), "HB" : 2 * lev, "RES" : int(lev/3), "STR" : int(lev/2), "DEX" : int(lev/3), "SPD" : int(lev/4), "MAG" : 0, "RTM" : int(lev/6)} for lev in range(1, 21)}                        
        self.bonus.update(self.level_bonus[1])
        
        
class Assassin(Job):
    def __init__(self):
        super(Assassin, self).__init__(name = "Assassin", description = "The hideous Assassin", abilities = {"offense" :  ability.Poison(), "support" :  ability.Shock()}, strategy = strategy.Aggressive())
                            
        self.level_bonus = {lev : {"MP" : int(lev/2), "HP" : 2* (lev-1), "HB" : 2 * lev, "RES" : 0, "STR" : int(lev/3), "DEX" : int(lev/2), "SPD" : 1 + int(lev/2), "MAG" : 0, "RTM" : int(lev/4)} for lev in range(1, 21)}                     
        self.bonus.update(self.level_bonus[1])
                
 
def get_jobs():
    return [Student(), Wanderer(), Protector(), Barbarian(), Assassin()]       
    
       

