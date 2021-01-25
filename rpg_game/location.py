import entity
from rpg_game.utils import nested_dict
from rpg_game.constants import *
import character, item
import copy, random, math





"""COORDINATES:
    |    y
   - ---->
    |
    |
    |
    v x
"""
class Location(object):
    def __init__(self, _height=3):
        self.events = {}
        self.height = _height
        self.entities = {}
        self.content = nested_dict()
        self.redraw = False

    @property
    def all(self):
        return [ent for k, ent in self.entities.items()]

    def on_update(self, _deltatime):
        for _id, ent in self.entities.copy().items():
            ent.on_update(_deltatime) 

    def update_content(self, _entity):
        pass   


class Inventory(Location):
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs, _height=1)
        for x in range(INVENTORY_SIZE):
            self.content[x] = None
        self.selection = None

    @property
    def encumbrance(self):
        return sum(i.encumbrance for n, i in self.content.items() if i)
    
    def has_free_spot(self):
        _spot = next((x  for x in self.content if not self.content[x]), -1)
        if _spot == -1:
            return False
        return True 

    def get(self, position):
        if position in self.content:
            return self.content[position]
        return None

    def free_position(self):
        _spot = next((x  for x in self.content if not self.content[x]), -1)
        if _spot > -1:
            return _spot
        return None

    def register(self, _entity):
        """register content"""
        if not _entity.id in self.entities:
            self.entities[_entity.id] = _entity
        x, y, z = _entity.position
        self.content[x] = _entity

    def unregister(self, _entity):
        """register content"""
        x, y, z = _entity.position
        self.content[x] = None 
        if _entity.id in self.entities:
            del self.entities[_entity.id]

    def add(self, obj):
        _spot = next((x for x in self.content if not self.content[x]), -1)
        if _spot > -1:
            obj.change_location((_spot, 0, 0), self)

    def remove(self, obj):
        self.unregister(obj)


class Room(Location):
    def __init__(self, name, world, _map):
        super().__init__()
        self.name = name
        self.world = world
        
        raw_map = [l for l in _map.split("\n") if l]
        X = len(raw_map)
        Y = max([len(l) for l in raw_map])
        self.container = [[" " for _ in range(Y)] for _ in range(X)]
        self.register_raw_map(raw_map)
        self.map = self.map_from_entities()

    @property
    def characters(self):
        return [ent for k, ent in self.entities.items() if isinstance(ent, character.Character)]

    def get(self, position):
        x, y, z = position
        if x in self.content and y in self.content[x] and z in self.content[x][y]:
            return self.content[x][y][z]
        return None

    def map_from_entities(self):
        _map = copy.deepcopy(self.container)
        for k, ent in self.entities.items():
            for m, p in zip(ent.marker, ent.positions):
                x, y, z = p
                max_z = max([z for z in self.content[x][y]], default=-1)
                if z == max_z and self.content[x][y][z] is ent:
                    _map[x][y] = (ent.color, m)
        return _map

    def layer_from_entities(self, _layer, debug=False):
        _map = copy.deepcopy(self.container)
        for k, ent in self.entities.items():
            for m, p in zip(ent.marker, ent.positions):
                x, y, z = p
                if z == _layer and self.content[x][y][z] is ent:
                    if debug:
                        _map[x][y] = (ent.color, type(ent).__name__[0])
                    else:
                        _map[x][y] = (ent.color, m)
        return _map

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        if self.redraw:
            self.map = self.map_from_entities()

    def update_content(self, _entity):
        for x, y, z in _entity.last_positions:
            if z in self.content[x][y] and self.content[x][y][z] is _entity:
                del self.content[x][y][z]
        for x, y, z in _entity.positions:
            self.content[x][y][z] = _entity
        self.redraw = True

    def register(self, _entity):
        """register content"""
        if not _entity.id in self.entities:
            self.entities[_entity.id] = _entity
            self.update_content(_entity)

    def unregister(self, _entity):
        """register content"""
        for x, y, z in _entity.positions:
            if z in self.content[x][y] and self.content[x][y][z] is _entity:
                del self.content[x][y][z]
        if _entity.id in self.entities:
            del self.entities[_entity.id]
        self.redraw = True

    def register_raw_map(self, raw_map):
        for x in range(len(self.container)):
            for y in range(len(self.container[x])):
                _marker = raw_map[x][y]
                if _marker != " ":
                    #here it could be possible to add special characters for montesrs, items, etc...
                    #or thin vs thick walls
                    if _marker == "░":
                        entity.Portal(_location=self, _position=(x, y, 0), _marker=_marker)
                    elif _marker in "┘┐┌└┤┴┬├─│┼":
                        entity.ThinWall(_location=self, _position=(x, y, 0), _marker=_marker)
                    elif _marker in "═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬●■." or _marker.isalnum():
                        entity.HardWall(_location=self, _position=(x, y, 0), _marker=_marker)
                    else:
                        entity.Empty(_location=self, _position=(x, y, 0), _marker=_marker)

    def free_position(self, _entity):
        _layer = _entity.layer
        _extra_positions = _entity.extra_positions
        pos = self.all_free_position(_layer, _extra_positions)
        if pos:
            return random.sample(pos, 1)[0]
        return None

    def all_free_position(self, _layer, _extra_positions):
        _free = []
        for x in range(len(self.container)):
            for y in range(len(self.container[x])):
                _all = [(x+xp, y+yp, _layer+zp) for xp, yp, zp in [(0,0,0)] + _extra_positions]
                if all(self.is_empty((xp, yp, zp)) for xp, yp, zp in _all):
                    _free.append((x, y, _layer))
        return _free

    def out_of_bounds(self, position):
        x, y, z = position
        return x < 0 or x >= len(self.container) or y < 0 or y >= len(self.container[x]) or z < 0 or z >= self.height

    def is_empty(self, position):
        x, y, z = position
        if self.out_of_bounds(position):
            return False
        return not bool(self.get(position))


            
        
     