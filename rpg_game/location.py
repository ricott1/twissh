from rpg_game.entity import Wall
import numpy as np

class Location(object):
    def __init__(self, _height=3):
        self.content = []
        self.events = {}
        self.redraw = False
        self.height = _height

    @property
    def all(self):
        _all = []
        for x in range(len(self.content)):
            for y in range(len(self.content[x])):
                for z in range(len(self.content[x][y])):
                    if self.content[x][y][z]:
                        _all.append(self.content[y][x][z])
        return set(_all)

    def clear(self, position):
        """clear content"""
        x, y, z = position
        if self.get((x, y, z)):
            self.redraw = True
        self.content[x][y][z] = None

    def register(self, content):
        """register content"""
        x, y, z = content.position
        #in the future use content.layer
        self.content[x][y][z] = content
        for xp, yp, zp in content.extra_position:
            self.content[x+xp][y+yp][z+zp] = content
        self.redraw = True

    def unregister(self, content):
        """register content"""
        self.clear(content.position)
        for xp, yp, zp in content.extra_position:
            self.clear((x+xp, y+yp, z+zp))

    def get(self, position):
        x, y, z = position
        try:
            return self.content[x][y][z]
        except IndexError:
            return None

    def is_empty(self, position):
        return not bool(self.get(position))

    def on_update(self):
        pass

    def free_position(self, _layer=1, _extra_position=[]):
        for x in range(len(self.content)):
            for y in range(len(self.content[x])):
                _all = [(x, y, _layer)] + _extra_position
                if all(self.is_empty((xp, yp, zp)) for (xp, yp, zp) in _all):
                    return (x, y, _layer)
        else:
            return None


class Inventory(Location):
    def __init__(self, size):
        super().__init__(_height=1)
        self.size = size
        self.content = [[[None for _ in range(self.height)] for _ in range(self.size)] for _ in range(self.size)]
        

class Room(Location):
    def __init__(self, name, _map):
        super().__init__()
        self.name = name
        self.raw_map = [l for l in _map.split("\n") if l]
        
        X = len(self.raw_map)
        Y = max([len(l) for l in self.raw_map])
        self.content = [[[None for _ in range(self.height)] for _ in range(Y)] for _ in range(X)]
        self.register_content()

        self.map = self.map_from_content()

    def register_content(self):
        for x in range(len(self.content)):
            for y in range(len(self.content[x])):
                _marker = self.raw_map[x][y]
                # print(x, y, _marker)
                if _marker != " ":
                    #here it could be possible to add special characters for montesrs, items, etc...
                    #or thin vs thick walls
                    w = Wall(_location=self, _position=(x, y, 0), _extra_position=[(0,0,1), (0,0,2)], _marker=_marker)

    def map_from_content(self):
        _map = []
        for x in range(len(self.content)):
            _line = []
            for y in range(len(self.content[x])):
                non_empty = [z for z in range(len(self.content[x][y])) if not self.is_empty((x, y, z))]
                #print("NONEMPRTY", x, y, non_empty)
                if non_empty:
                    #show top marker
                    z = max(non_empty)
                    _line.append(self.get((x, y, z)).marker)
                else:
                    _line.append(" ")
            _map.append(_line) 
        return _map

    def forward(self, position, direction):
        x, y, z = position
        new_x = x + int(direction=="down") - int(direction=="up")
        new_y = y + int(direction=="right") - int(direction=="left")
        return (new_x, new_y, z)

    def on_update(self):
        if self.redraw:
            self.redraw = False
            self.map = self.map_from_content()
        
     