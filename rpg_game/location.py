import os

class Wall(object):
    def __init__(self, x, y, marker):
        self.position = (x, y)
        self.marker = None

class Location(object):
    def __init__(self, name, _map):
        self.name = name
        self.map = _map
        self.map_content = [[None  if l == " " else Wall(x, y, _map[y][x]) for x, l in enumerate(line)] for y, line in enumerate(_map)]
        self.visible_map = self.map
        self.characters = []
        self.events = {} #key = event, value = switch
        self.inventory = []
        self.has_changed = False

    def update_visible_map(self):
        if self.has_changed:
            self.has_changed = False

            self.visible_map = []
            #update to have colors to markers depending on object
            for cont, line in zip(self.map_content, self.map):
                for i, c in enumerate(cont):
                    if c == self:
                        line = line[:i] +  c.marker + line[i + 1:]
                    elif c and c.marker:
                        line = line[:i] +  c.marker + line[i + 1:]
                self.visible_map.append(line)
        
     