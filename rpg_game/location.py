from rpg_game.entity import Wall
import numpy as np
import copy, collections, random

nested_dict = lambda: collections.defaultdict(nested_dict)

class Location(object):
    def __init__(self, _height=3):
        self.content = nested_dict()
        self.container = []
        self.events = {}
        self.redraw = False
        self.height = _height
        self.entities = {}

    @property
    def all(self):
        return [ent for k, ent in self.entities.items()]

    def register(self, obj):
        """register content"""
        self.redraw = True
        if not obj.id in self.entities:
            self.entities[obj.id] = obj
            for x, y, z in obj.positions:
                self.content[x][y][z] = obj

    def unregister(self, obj):
        """register content"""
        self.redraw = True
        if obj.id in self.entities:
            del self.entities[obj.id]
            for x, y, z in obj.positions:
                if z in self.content[x][y]:
                    del self.content[x][y][z]

    def get(self, position):
        x, y, z = position
        if z in self.content[x][y]:
            return self.content[x][y][z]
        return None

    def is_empty(self, position):
        x, y, z = position
        return not z in self.content[x][y]

    def on_update(self, _deltatime):
        for _id, e in list(self.entities.items()):
            e.on_update(_deltatime)
        self.redraw = self.redraw or any(e.redraw for key, e in self.entities.items())

    def free_position(self, _layer, _extra_position=[]):
        pos = self.all_free_position(_layer, _extra_position)
        if pos:
            return random.sample(pos, 1)[0]
        return None

    def all_free_position(self, _layer, _extra_position):
        _free = []
        for x in range(len(self.container)):
            for y in range(len(self.container[x])):
                _all = [(x, y, _layer)] + [(x+xp, y+yp, _layer+zp) for xp, yp, zp in [(0,0,0)] + _extra_position]
                if all(self.is_empty((xp, yp, zp)) for xp, yp, zp in _all):
                    _free.append((x, y, _layer))
        return _free

class Inventory(Location):
    def __init__(self, size):
        super().__init__(_height=1)
        self.size = size
        self.container = [[" " for _ in range(self.size)] for _ in range(self.height)]

class Room(Location):
    def __init__(self, name, _map):
        super().__init__()
        self.name = name
        raw_map = [l for l in _map.split("\n") if l]
        X = len(raw_map)
        Y = max([len(l) for l in raw_map])
        self.container = [[" " for _ in range(Y)] for _ in range(X)]
        self.register_raw_map(raw_map)
        self.content = self.content_from_entities()
        self.map = self.map_from_entities()

    def register_raw_map(self, raw_map):
        for x in range(len(self.container)):
            for y in range(len(self.container[x])):
                _marker = raw_map[x][y]
                # print(x, y, _marker)
                if _marker != " ":
                    #here it could be possible to add special characters for montesrs, items, etc...
                    #or thin vs thick walls
                    w = Wall(_location=self, _position=(x, y, 0), _extra_position=[(0,0,1), (0,0,2)], _marker=_marker)

    def map_from_entities(self):
        _map = copy.deepcopy(self.container)
        for k, ent in self.entities.items():
            for m, p in zip(ent.marker, ent.positions):
                x, y, z = p
                max_z = max([z for z in self.content[x][y]])
                if z == max_z:
                    _map[x][y] = m
        return _map

    def content_from_entities(self):
        _content = nested_dict()
        for k, ent in self.entities.items():
            for x, y, z in ent.positions:
                _content[x][y][z] = ent
        return _content

    def on_update(self, DELTATIME):
        super().on_update(DELTATIME)
        if self.redraw:
            self.content = self.content_from_entities()
            self.map = self.map_from_entities()
        
     