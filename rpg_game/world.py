from os import walk
import os
import location, character, random, uuid, item, race, job, inventory

RANDOM_NAMES = ("Gimmi", "Renny","Hop","Hip", "Cat", "Batman", "Yitterium", "Micha","Reynolds","Giangi","Paolino","Ventura","Mariachi","Favetti","Orleo","Bissaglia", "Fonzie","Alvarez","Selenio","Paul","Fedor","Gutierrez","Raul Bravo","Ricardo","Lopez","Figueroa","Beniamino", "Gino","Yasser","Gandalf","Komeini","Blasfy","Misfit","Pinto","Cucchi","Monty","Python","Fia Mei","Sean Penn","Pio Nono","Fau","Tella","Suarez","Hannibal","Maori")

class World(object):
    def __init__(self):
        self.locations = []
        self.locations.append(quick_room(self, "base", map_from_file()))

    def update_visible_maps(self):
        for l in self.locations:
            l.update_visible_map()


def quick_room(world, name, _map): 
    r = location.Location(name, _map)
    #r.inventory.append(inventory.FuryArmor(location = r))
    r.inventory.append(inventory.ChainArmor(location = r))
    r.inventory.append(inventory.LongSword(location = r))
    #r.inventory.append(inventory.GreatAxe(location = r))
    #r.inventory.append(inventory.BeltOfGiants(location = r))
    r.inventory.append(inventory.HelmOfContinency(location = r))
    r.inventory.append(inventory.JacksonHelm(location = r))
    r.inventory.append(inventory.JacksonBelt(location = r))
    r.inventory.append(inventory.JacksonBoots(location = r))
    for i in range(random.randint(0,1)):
        v = quick_villain()
        v.location = r
        v.world = world
        r.characters.append(v)
    return r
        
def quick_villain(r = 'random', j = 'random'):
    MP, RES, MAG, SPD, DEX, STR = [sum(sorted([random.randint(1,6) for l in range(4)])[1:]) -2 for x in range(6)]
    HP = 4 + 2* random.randint(0,3)
    HB = 30 + random.randint(1, 30)
    RTM = random.randint(1,2)
    data = {"name" : random.sample(RANDOM_NAMES, 1)[0], "MP" : MP + 6,  "HB" : HB + 30, "RES" : RES, "MAG" : MAG, "HP" : HP + 4, "SPD" : SPD, "DEX" : DEX + 6, "STR" : STR + 6, 
    "RTM" : RTM}
    
    races = race.get_monster_races()
    all_races = race.get_races()
    if [rac for rac in all_races if rac.name == r]:
        prace = random.sample([rac for rac in all_races if rac.name == r], 1)[0]
    else:
        prace = random.sample(races, 1)[0]
    jobs = job.get_jobs()
    if [jo for jo in jobs if jo.name == j]:
        pjob = random.sample([jo for jo in jobs if jo.name == j], 1)[0]
    else:
        pjob = random.sample(jobs, 1)[0] 
    
    return character.Villain(uuid.uuid4(), data)   

def map_from_file(filename = "map.txt"):
    map_path = "/Users/alessandro.ricottone/Desktop/personal/coding/twissh/twissh/rpg_game/"
    with open(map_path + filename, "r") as f:
        _map = f.readlines()
    return [line.rstrip('\n') for line in _map]

def map_starting_position(_map):
    for y, m in enumerate(_map):
        x = m.find("P")
        if x >= 0: 
            return (x, y)
    return (0, 0)

if __name__ == "__main__":
    w = World()
