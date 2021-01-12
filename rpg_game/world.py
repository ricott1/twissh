import os
import location, character, random, item, inventory, bestiary, entity
from rpg_game.utils import random_stats, random_name
from rpg_game.world_map import *


class World(object):
    def __init__(self):
        self.locations = {
            "ground-zero" : quick_room(self, "Ground Zero", world_map),
            "floor-0" : quick_room(self, "Ground Floor", floor_0),
            "floor-1" : quick_room(self, "First Floor", floor_1),
            "floor-2" : quick_room(self, "Top Floor", floor_2)
        }
        self.link_portals()

    def on_update(self, _deltatime):
        for l, loc in self.locations.items():
            loc.on_update(_deltatime)

    def starting_location(self):
        return self.locations["floor-0"]

    def link_portals(self):
        _portals = [ent for l in self.locations for ent in self.locations[l].all  if isinstance(ent, entity.Portal)]
        for p in _portals:
            for q in [r for r in _portals if r is not p]:
                if p.position == q.position:
                    p.partner = q
                    q.partner = p


def quick_room(world, name, _map): 
    r = location.Room(name, world, _map)
    inventory.longSword(_location=r)
    inventory.longBow(_location=r)
    inventory.rovaisThorn(_location=r)
    inventory.chainArmor(_location=r)
    inventory.buckler(_location=r)
    inventory.chiappilArmor(_location=r)

    
    bestiary.Goblin(_name="Gulluk", _stats=random_stats(), _location = r)
    bestiary.Goblin(_name="Gallog", _stats=random_stats(), _location = r)
    #ogre = bestiary.Ogre(_stats=random_stats(), _location = r)
    #bestiary.Dragon(_name="Paco", _stats=random_stats(), _location = r)
    
    return r
