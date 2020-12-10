import os

class Empty(object):
    def __init__(self, x, y, marker):
        self.position = (x, y)
        self.marker = " "

class Wall(object):
    def __init__(self, x, y, marker):
        self.position = (x, y)
        self.marker = marker
        self.HP = 100

class Location(object):
    def __init__(self):
        self.content = []
        self.events = {}
        self.redraw = False

    def clear(self, position, layer):
        """clear content"""
        x, y = position
        del self.content[y][x][layer]
        self.redraw = True

    def register(self, content):
        """register content"""
        x, y = content.position
        #in the future use content.layer
        self.content[y][x][content.layer] = content
        self.redraw = True

    def is_empty(self, position, layer):
        x, y = position
        if layer not in self.content[y][x]:
            return True
        if self.content[y][x][layer]:
            return False
        return True

    def on_update(self):
        pass


class Room(Location):
    def __init__(self, name, _map):
        super().__init__()
        self.name = name
        self.raw_map = _map
        #each square of the map can contain something on several layers: 0 for pickable items, 1 for living bodies, 2 for flying etc...
        # self.content = [[{}  if l == " " else {1 : Wall(x, y, _map[y][x])} for x, l in enumerate(line)] for y, line in enumerate(_map)]
        for y, line in enumerate(_map):
            _line = []
            for x, l in enumerate(line):
                _l = {}
                if l != " ":
                    w = Wall(x, y, _map[y][x])
                    _l = {0: w, 1 : w, 2: w}
                _line.append(_l)
            self.content.append(_line)


        self.map = self.raw_map

    def on_update(self):
        if self.redraw:
            self.redraw = False
            self.map = []
            #update to have colors to markers depending on object
            # for cont, line in zip(self.content, self.raw_map):
            #     for i, c in enumerate(cont):
            #         if c:
            #             #show only the content on top layer
            #             max_layer = max([key for key, value in c.items()])
            #             if max_layer and c[max_layer].marker:
            #                 line = line[:i] +  c[max_layer].marker + line[i + 1:]
            #     self.map.append(line)
            for line in self.content:
                _line = ""
                for i, content in enumerate(line):
                    if content:
                        #show only the content on top layer
                        max_layer = max([key for key, value in content.items()])
                        _line += content[max_layer].marker
                    else:
                        _line += " "
                self.map.append(_line)
        
     