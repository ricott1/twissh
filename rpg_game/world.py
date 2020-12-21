import os
import location, character, random, item, inventory
from rpg_game.utils import random_stats, random_name
from rpg_game.world_map import world_map

class World(object):
    def __init__(self):
        self.locations = []
        self.locations.append(quick_room(self, "base", world_map))

    def on_update(self):
        for l in self.locations:
            l.on_update()

def add_inventory(inv, room):
    inv.location = room
    free = [(i, j) for j, line in enumerate(room.content) for i, l in enumerate(line)  if not l]
    x, y = random.choice(free)
    inv.position = (x, y, 0)
    room.register(inv)

def quick_room(world, name, _map): 
    r = location.Room(name, _map)
    long_sword = inventory.LongSword(_location=r)
    chain_armor = inventory.ChainArmor(_location=r)
    
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
    v = quick_villain(_location = r)
    return r

def quick_villain(_location = None):
    return character.Villain(_name=random_name(), _stats=random_stats(), _location = _location)

# def map_from_file(filename = "map.txt"):
#     _map = world_map.split('\n')
#     return [line.rstrip('\n') for line in _map]
