import os, random
import location, character, item, inventory, bestiary, entity
from rpg_game.utils import random_stats, random_name
from rpg_game.world_map import *


class World(object):
    def __init__(self):
        self.locations = {
            "base" : quick_room(self, "Base", base, _common_loot_prob=1, _monster_prob=0),
            "floor-0" : quick_room(self, "Ground Floor", floor_0),
            "floor-1" : quick_room(self, "First Floor", floor_1, _uncommon_loot_prob=0.5, _rare_loot_prob=0.25),
            "floor-2" : quick_room(self, "Top Floor", floor_2, _unique_loot_prob=1)
        }
        self.link_portals()

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


def quick_room(world, name, _map, _common_loot_prob=0.5, _uncommon_loot_prob=0.25, _rare_loot_prob=0.1, _unique_loot_prob=0.003, _monster_prob=0.9): 
    r = location.Room(name, world, _map)
    if random.random()< _common_loot_prob:
        inventory.longSword(_location=r)
    if random.random()< _common_loot_prob:
        inventory.warHammer(_location=r)
    if random.random()< _common_loot_prob:
        inventory.chainArmor(_location=r)
    if random.random()< _common_loot_prob:
        inventory.buckler(_location=r)
    if random.random()< _common_loot_prob:
        inventory.healingPotion(_location=r)

    if random.random()< _uncommon_loot_prob:
        inventory.longBow(_location=r)

    if random.random()< _rare_loot_prob:
        inventory.rovaisThorn(_location=r)
    
    if random.random()< _unique_loot_prob:
        inventory.chiappilArmor(_location=r)
    
    if random.random()< _monster_prob:
        bestiary.Goblin(_name="Gulluk", _stats=random_stats(), _location = r)
    if random.random()< _monster_prob:
        bestiary.Goblin(_name="Gallog", _stats=random_stats(), _location = r)
    if random.random()< _monster_prob:
        bestiary.Goblin(_name="Gellac", _stats=random_stats(), _location = r)
    #ogre = bestiary.Ogre(_stats=random_stats(), _location = r)
    #bestiary.Dragon(_name="Paco", _stats=random_stats(), _location = r)
    
    return r
