import random, item
class Mission(object):
    def __init__(self, protagonist):
        self.name = ''
        self.protagonist = protagonist
        self.description = ''
        self.goal = None
    def requisites(self, *args):
        return True    
    def on_start(self, *args):
        pass
    def on_update(self, *args):
        pass
    def on_end(self, *args):
        for p in self.protagonist.players:
            p.add_experience(self.exp) 
        self.protagonist.data["mission"].append(self.id)
        

        
class FindDreamStone(Mission):
    def __init__(self, protagonist):
        self.protagonist = protagonist
        self.name = "Find the dream stone"
        self.id = "f1"
        self.exp = 1000
        
        self.goals = ["Find a room containing a dream stone by exploring the file system", "Create a dream file and dream!", "Find a room containing a dimensional warp by exploring the file system", "Create a warp file to bring your dream into your world", "Mission accomplished!"]
        self.description = self.goals[0]
        
    def on_update(self):
        if self.description == self.goals[0] and self.protagonist.players[0].location.dream_stone:
            self.description = self.goals[1]
        elif self.description == self.goals[1] and len(self.protagonist.players) > 1:
            self.description = self.goals[2] 
        elif self.description == self.goals[2] and self.protagonist.players[0].location.dimensional_warp:
            self.description = self.goals[3]
        elif self.description == self.goals[3] and self.protagonist.players[0].location == self.protagonist.players[1].location: 
            self.description = self.goals[4]
            self.on_end()
        
class KillTheDragon(Mission):
    def __init__(self, protagonist):
        self.protagonist = protagonist
        self.name = "Kill the dragon"
        self.id = "k1"
        self.exp = 2000
        
        self.goals = ["Find the Dragon", "Kill him", "Mission accomplished!"]
        self.description = self.goals[0]
        self.dragon = False

    def requisites(self):
        if len(self.protagonist.players[0].world.locations) > 4 and self.protagonist.players[0].level > 3:
            return True
        return False    
    def on_start(self):
        if not self.dragon:
            world = self.protagonist.players[0].world
            v = world.quick_villain(r = "Dragon")
            l = random.sample([loc for loc in world.locations if self.protagonist.players[0].location != loc], 1)[0]
            v.location = l
            v.master_location_path = v.location.path
            v.world = world
            l.characters.append(v)
            self.dragon = v
    def on_update(self):
        if self.description == self.goals[0] and self.protagonist.players[0].location == self.dragon.location:#any(c.race.name == "Dragon" for c in self.protagonist.players[0].location.characters):
            self.description = self.goals[1]
        elif self.description == self.goals[1] and self.dragon.is_dead:
            self.description = self.goals[2] 
        
            self.on_end()
 
class FindTheMagicSword(Mission):
    def __init__(self, protagonist):
        self.protagonist = protagonist
        self.name = "Find the magic sword"
        self.id = "f2"
        self.exp = 2000
        
        self.goals = ["Find the magic sword", "Pick it up", "Mission accomplished!"]
        self.description = self.goals[0]
        self.sword = False

    def requisites(self):
        if len(self.protagonist.players[0].world.locations) >= 6 and self.protagonist.players[0].level > 2:
            return True
        return False    
    def on_start(self):
        if not self.sword:
            world = self.protagonist.players[0].world
            l = random.sample([loc for loc in world.locations if self.protagonist.players[0].location != loc], 1)[0]
            self.sword = item.Weapon(name="Magic Sword", description="The magic is in you", bonus = {'STR':1}, damage=6, dices = 2, location =l)
            l.inventory.append(self.sword)
            
    def on_update(self):
        if self.description == self.goals[0] and self.protagonist.players[0].location == self.sword.location:
            self.description = self.goals[1]
        elif self.description == self.goals[1] and self.sword.location == self.protagonist.players[0]:
            self.description = self.goals[2] 
        
            self.on_end()      

class KillTheGoblins(Mission):
    def __init__(self, protagonist):
        self.protagonist = protagonist
        self.name = "Kill all the goblins!"
        self.id = "k2"
        self.exp = 2000
        self.goblins = []
        self.goals = ["Kill all the golbins in the filesystem ({} remaining)".format(len(self.goblins)), "Mission accomplished!"]
        self.description = self.goals[0]
        

    def requisites(self):
        if len(self.protagonist.players[0].world.locations) >= 10 and self.protagonist.players[0].level > 1:
            return True
        return False    
    def on_start(self):
        if not self.goblins:
            world = self.protagonist.players[0].world
            for n in range(10):
                g = world.quick_villain(r = "Goblin")
                l = random.sample([loc for loc in world.locations if self.protagonist.players[0].location != loc], 1)[0]
                g.location = l
                g.master_location_path = g.location.path
                g.world = world
                l.characters.append(g)
                self.goblins.append(g)
                
    def on_update(self):
        for g in self.goblins:
            if g.is_dead:
                self.goblins.remove(g)
        self.description = "Kill all the golbins in the filesystem ({} remaining)".format(len(self.goblins))
        if len(self.goblins) == 0:
            self.description = self.goals[1] 
        
            self.on_end()        
        
def get_missions(protagonist):
    return {"f1" : FindDreamStone(protagonist),"f2" : FindTheMagicSword(protagonist),"k1":KillTheDragon(protagonist), "k2" : KillTheGoblins(protagonist)}   
