import ability
#"shock" : 0, "mute" : 0, "dream" :0, "death" : 0
class Race(object):
    def __init__(self, name="", description="", inventory=[], abilities={}, 
                immunities={}, bonus={"MP" : 0, "HP" : 0, "HB" : 0, "RES" : 0, "STR" : 0, "DEX" : 0, "SPD" : 0, "MAG" : 0, "RTM" : 0, "AC" : 0}):
        self.name = name
        self.description = description
        self.inventory = inventory
        self.abilities = abilities
        self.immunities = immunities
        self.bonus = {"MP" : 0, "HP" : 0, "HB" : 0, "RES" : 0, "STR" : 0, "DEX" : 0, "SPD" : 0, "MAG" : 0, "RTM" : 0, "AC" : 0}
        self.bonus.update(bonus)
    def on_update(self, *args):
        pass   
        
class Human(Race):
    def __init__(self):
        super(Human, self).__init__(name = "Human", description = "A humanoid", bonus = {"MP" : 2, "HP" : 2, "RES" : 1, "STR" : 1, "DEX" : 1, "SPD" : 1, "MAG" : 1})
             
class Elf(Race):
    def __init__(self):
        super(Elf, self).__init__(name = "Elf", description = "An elf", immunities = {"mute" : -1}, 
                                 bonus = {"MP" : 2, "HB" : -2, "DEX" : 2, "SPD" : 2, "RTM" : 1})
class Dwarf(Race):
    def __init__(self):
        super(Dwarf, self).__init__(name = "Dwarf", description = "A bearded dwarf", immunities = {"shock" : -1}, 
                                 bonus = {"HP" : 4, "RES" : 2, "STR" : 2, "DEX" : 0, "MAG" : -2})
                                      
class Monster(Race):
    def __init__(self):
        super(Monster, self).__init__(name = "Monster", description = "A horrible monster", immunities = {}, 
                                 bonus = {"HP" : 2, "HB" : 4, "RES" : 1, "STR" : 2, "DEX" : 1})
                                 
class Goblin(Race):
    def __init__(self):
        super(Goblin, self).__init__(name = "Goblin", description = "A greeny goblin", immunities = {"shock" : -1}, 
                                 bonus = {"HP" : 2, "HB" : 8, "SPD" : 2})
    
class Dragon(Race):
    def __init__(self):
        super(Dragon, self).__init__(name = "Dragon", description = "The legendary dragon", abilities = {"race special" : ability.Breath()}, immunities = {"shock" : -1, "mute" : -1, "dream" :-1},
                                    bonus = {"MP" : 10, "HP" : 20, "HB" : -10, "RES" : 4, "STR" : 4, "MAG" : 4, "RTM" : 2})
       
 
def get_races():
    return [Human(), Elf(), Dwarf(), Monster(), Dragon(), Goblin()]
    
def get_player_races():
    return [Human(), Elf(), Dwarf()]

def get_monster_races():
    return [Human(), Elf(), Dwarf(), Monster()]
        

