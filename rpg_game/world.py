import os
import location, character, random, item, inventory, bestiary
from rpg_game.utils import random_stats, random_name
from rpg_game.world_map import world_map


class World(object):
    def __init__(self):
        self.locations = []
        self.locations.append(quick_room(self, "base", world_map))
        self.redraw = False

    def on_update(self, _deltatime):
        self.redraw = False
        for l in self.locations:
            l.on_update(_deltatime)
        self.redraw = any(l.redraw for l in self.locations)
        for l in self.locations:
            l.redraw = False

def quick_room(world, name, _map): 
    r = location.Room(name, _map)
    long_sword = inventory.LongSword(_location=r)
    long_bow = inventory.LongBow(_location=r)
    s_s = inventory.RovaisThorn(_location=r)
    chain_armor = inventory.ChainArmor(_location=r)
    buckler = inventory.Buckler(_location=r)
    chiappil_armor = inventory.ChiappilArmor(_location=r)

    
    goblin = bestiary.Goblin(_stats=random_stats(), _location = r)
    goblin2 = bestiary.Goblin(_stats=random_stats(), _location = r)
    #ogre = bestiary.Ogre(_stats=random_stats(), _location = r)
    #dragon = bestiary.Dragon(_stats=random_stats(), _location = r)
    
    return r
