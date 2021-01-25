import os, random
import location, character, item, armory, bestiary, entity
from rpg_game.utils import random_stats, random_name
from rpg_game.world_map import *


class World(object):
    def __init__(self):
        self.locations = {
            "base" : quick_room(self, "Base", base, {"common":1, "uncommon":0.01, "rare":0}, _monster_prob=0),
            "floor-0" : quick_room(self, "Ground Floor", floor_0, {"common":0.5, "uncommon":0.25, "rare":0.1}),
            "floor-1" : quick_room(self, "First Floor", floor_1, {"common":0.35, "uncommon":0.65, "rare":0.25}),
            "floor-2" : quick_room(self, "Top Floor", floor_2, {"common":0, "uncommon":0, "rare":0.5})
        }
        self.link_portals()
        
        for i in armory.unique_inventory():
            i(_location=self.starting_location()) 

    def on_update(self, _deltatime):
        for l, loc in self.locations.items():
            loc.on_update(_deltatime)

    def starting_location(self):
        return self.locations["base"]

    def link_portals(self):
        _portals = [ent for l in self.locations for ent in self.locations[l].all  if isinstance(ent, entity.Portal)]
        for p in _portals:
            for q in [r for r in _portals if r is not p]:
                if p.position == q.position:
                    p.partner = q
                    q.partner = p 

    def create_topology(self):
        pass


def quick_room(world, name, _map, loot_prob, _monster_prob=0.9): 
    r = location.Room(name, world, _map)

    for rarity, item_list in armory.inventory_list().items():
        for i in item_list:
            if random.random()< loot_prob[rarity]:
                i(_location=r) 
    
    if random.random()< _monster_prob:
        bestiary.goblin(_name="Gulluk", _stats=random_stats(), _location = r)
    if random.random()< _monster_prob:
        bestiary.goblin(_name="Gallog", _stats=random_stats(), _location = r)
    if random.random()< _monster_prob:
        bestiary.goblin(_name="Gellac", _stats=random_stats(), _location = r)
    #ogre = bestiary.Ogre(_stats=random_stats(), _location = r)
    #bestiary.Dragon(_name="Paco", _stats=random_stats(), _location = r)
    
    return r
