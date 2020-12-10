from os import walk
import os
import location, character, random, uuid, item, race, job, inventory
from rpg_game.utils import quick_data, new_id

RANDOM_NAMES = ("Gimmi", "Renny","Hop","Hip", "Cat", "Batman", "Yitterium", "Micha","Reynolds","Giangi","Paolino","Ventura","Mariachi","Favetti","Orleo","Bissaglia", "Fonzie","Alvarez","Selenio","Paul","Fedor","Gutierrez","Raul Bravo","Ricardo","Lopez","Figueroa","Beniamino", "Gino","Yasser","Gandalf","Komeini","Blasfy","Misfit","Pinto","Cucchi","Monty","Python","Fia Mei","Sean Penn","Pio Nono","Fau","Tella","Suarez","Hannibal","Maori")

class World(object):
    def __init__(self):
        self.locations = []
        self.locations.append(quick_room(self, "base", map_from_file()))

    def on_update(self):
        for l in self.locations:
            l.on_update()


def quick_room(world, name, _map): 
    
    r = location.Room(name, _map)
    sword = inventory.LongSword(location = r)
    free = [(i, j) for j, line in enumerate(r.content) for i, l in enumerate(line)  if not l]
    x, y = random.choice(free)
    sword.position = (x, y)
    r.register(sword)
    #r.inventory.append(inventory.FuryArmor(location = r))
    # r.inventory.append(inventory.ChainArmor(location = r))
    # r.inventory.append(inventory.LongSword(location = r))
    # #r.inventory.append(inventory.GreatAxe(location = r))
    # #r.inventory.append(inventory.BeltOfGiants(location = r))
    # r.inventory.append(inventory.HelmOfContinency(location = r))
    # r.inventory.append(inventory.JacksonHelm(location = r))
    # r.inventory.append(inventory.JacksonBelt(location = r))
    # r.inventory.append(inventory.JacksonBoots(location = r))
    # for i in range(random.randint(0,1)):
    v = quick_villain(location = r)
    r.register(v)
    return r

def quick_villain(location = None):
    return character.Villain(new_id(), quick_data(), location = location)

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
