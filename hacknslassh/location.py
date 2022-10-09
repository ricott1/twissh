from __future__ import annotations
from dataclasses import dataclass
import random
from hacknslassh.components.in_location import Markers
from hacknslassh.gui.utils import marker_to_urwid_text
from hacknslassh.utils import nested_dict
from hacknslassh.constants import *
from .components import InLocation
import urwid
import esper


"""COORDINATES:
    |    y
   - ---->
    |
    |
    |
    v x
"""


class Location(object):
    def __init__(self, max_x: int = 20, max_y: int = 80, max_z: int = 5) -> None:
        self.max_x = max_x
        self.max_y = max_y
        self.max_z = max_z
        self.floor_render_style = None
        self.wall_render_style = None
        self.empty_marker = "."
        self.content = nested_dict()
        self.urwid_text: list[tuple[urwid.AttrSpec, str] | str] = []
        self.base_map = [[" " for _ in range(self.max_y)] for _ in range(self.max_x)]
        self.map = [[" " for _ in range(self.max_y)] for _ in range(self.max_x)]
        
        # for x in range(self.max_x):
        #     self.map[x][0] = "l"
        #     self.map[x][self.max_y - 1] = "r"
        # for y in range(self.max_y):
        #     self.map[0][y] = "u"
        #     self.map[self.max_x-1][y] = "d"

    def generate_random_map(self, world: esper.World) -> list[Room]:
        rooms = []
        N = random.randint(6, 8)
        trials = 0
        max_height = max_width = 16
        min_height = min_width = 5
        while len(rooms) < N or trials < 100:
            min_x, max_x = sorted([random.randint(0, (self.max_x - 1)), random.randint(0, (self.max_x - 1))])
            min_y, max_y = sorted([random.randint(0, (self.max_y - 1)), random.randint(0, (self.max_y - 1))])
            if (max_x - min_x) < min_height or (max_x - min_x) > max_height or (max_y - min_y) < min_width or (max_y - min_y) > max_width:
                trials += 1
                continue
            room = Room(min_x, min_y, max_x, max_y)
            if not room.overlaps_with_any(rooms):
                rooms.append(room)
        
        # sort rooms left to right
        rooms = sorted(rooms, key= lambda r: r.min_y)

        corridors = []
        doors = []
        for i in range(len(rooms)-1):
            r1 = rooms[i]
            r2 = rooms[i + 1]
            top_room, bottom_room = (r1, r2) if r1.min_x < r2.min_x else (r2, r1)

            if not r1.overlaps_vertically(r2):
                corridor_y = random.randint(*sorted([r2.min_y + 1, min(r1.max_y, r2.max_y) - 3]))
                corridor = Room(top_room.max_x, corridor_y, bottom_room.min_x, corridor_y + 2)
                corridors.append(corridor)
                doors.append((corridor.max_x, corridor.min_y + 1, 1))
                doors.append((corridor.min_x, corridor.min_y + 1, 1))
            if not r1.overlaps_horizontally(r2):
                corridor_x = random.randint(*sorted([bottom_room.min_x + 1, min(top_room.max_x, bottom_room.max_x) - 3]))
                corridor = Room(corridor_x, r1.max_y, corridor_x + 2, r2.min_y)
                corridors.append(corridor)
                doors.append((corridor.min_x + 1, corridor.max_y, 1))
                doors.append((corridor.min_x + 1, corridor.min_y, 1))
        
        for room in rooms + corridors:
            for x in range(room.min_x, room.max_x + 1):
                self.set_renderable_entity(world, world.create_entity(InLocation(self, (x, room.min_y, 1), marker=Markers.WALL)))
                self.set_renderable_entity(world, world.create_entity(InLocation(self, (x, room.max_y, 1), marker=Markers.WALL)))
                # self.map[x][room.min_y] = "#"
                # self.map[x][room.max_y] = "#"
    
                for y in range(room.min_y + 1, room.max_y):
                    self.map[x][y] = self.empty_marker
            for y in range(room.min_y, room.max_y + 1):
                self.set_renderable_entity(world, world.create_entity(InLocation(self, (room.min_x, y, 1), marker=Markers.WALL)))
                self.set_renderable_entity(world, world.create_entity(InLocation(self, (room.max_x, y, 1), marker=Markers.WALL)))
                # self.map[room.min_x][y] = "#"
                # self.map[room.max_x][y] = "#"
        for d in doors:
            if wall_id := self.get_at(d):
                self.remove_renderable_entity(world, wall_id)
                world.delete_entity(wall_id)
        return rooms
        



    def is_in_bound(self, position: tuple) -> bool:
        x, y, z = position
        return x < self.max_x and y < self.max_y and z < self.max_z and x >= 0 and y >= 0 and z >= 0

    def max_z_at(self, position: tuple) -> int:
        x, y, _ = position
        if x in self.content and y in self.content[x]:
            return max([z for z in self.content[x][y]], default=-1)
        return -1
    
    def get_top_at(self, position: tuple) -> int:
        z = self.max_z_at(position)
        if z >= 0:
            x, y, _ = position
            return self.content[x][y][z]
        return 0
    
    def get_at(self, position: tuple) -> int | None:
        x, y, z = position
        if not self.is_in_bound(position):
            return None
        if x in self.content and y in self.content[x] and z in self.content[x][y]:
            return self.content[x][y][z]
        return None
    
    def set_at(self, position: tuple, ent_id: int) -> None:
        x, y, z = position
        if not self.is_in_bound(position):
            return
        if x not in self.content:
            self.content[x] = nested_dict()
        if y not in self.content[x]:
            self.content[x][y] = nested_dict()
        self.content[x][y][z] = ent_id

    def remove_at(self, position: tuple) -> None:
        x, y, z = position
        if x in self.content and y in self.content[x] and z in self.content[x][y]:
            del self.content[x][y][z]
    
    def set_renderable_entity(self, world: esper.World, ent_id: int) -> None:
        in_location = world.component_for_entity(ent_id, InLocation)
        position = in_location.position
        if not self.is_in_bound(position):
            return
        x, y, z = position
        
        if x not in self.content:
            self.content[x] = nested_dict()
        if y not in self.content[x]:
            self.content[x][y] = nested_dict()
        self.content[x][y][z] = ent_id
        if z == self.max_z_at(position):
            self.map[x][y] = marker_to_urwid_text(in_location.marker, in_location.fg, in_location.bg, in_location.visibility)

    def remove_renderable_entity(self, world: esper.World, ent_id: int) -> None:
        in_location = world.component_for_entity(ent_id, InLocation)
        position = in_location.position
        x, y, z = position
        if x in self.content and y in self.content[x] and z in self.content[x][y]:
            del self.content[x][y][z]
            if self.max_z_at(position) >= 0:
                top = world.component_for_entity(self.get_top_at(position), InLocation)
                self.map[x][y] = marker_to_urwid_text(top.marker, top.fg, top.bg, top.visibility)
            else:
                self.map[x][y] = self.empty_marker

@dataclass
class Room:
    min_x: int
    min_y: int
    max_x: int
    max_y: int
    min_z: int = 0
    max_z: int = 5

    @property
    def center(self) -> tuple:
        return (
            (self.min_x + self.max_x) // 2,
            (self.min_y + self.max_y) // 2,
            (self.min_z + self.max_z) // 2
        )
    
    def overlaps_horizontally(self, room: Room) -> bool:
        return  (
            self.min_y <= room.min_y <= self.max_y 
            or self.min_y <= room.max_y <= self.max_y
            or room.min_y <= self.min_y <= room.max_y 
            or room.min_y <= self.min_y <= room.max_y 
        )
    
    def overlaps_vertically(self, room: Room) -> bool:
        return (
            self.min_x <= room.min_x <= self.max_x 
            or self.min_x <= room.max_x <= self.max_x
            or room.min_x <= self.min_x <= room.max_x 
            or room.min_x <= self.min_x <= room.max_x 
        )

    def overlaps(self, room: Room) -> bool:
        return self.overlaps_horizontally(room) and self.overlaps_vertically(room)
    
    def overlaps_with_any(self, rooms: list[Room]) -> bool:
        for room in rooms:
            if self.overlaps(room):
                return True
        return False
    

# class Location(object):
#     def __init__(self, _height=3):
#         self.events = {}
#         self.height = _height
#         self.entities = {}
#         self.content = nested_dict()
#         self.redraw = False

#     @property
#     def all(self):
#         return [ent for k, ent in self.entities.items()]

#     def on_update(self, _deltatime):
#         for _id, ent in self.entities.copy().items():
#             ent.on_update(_deltatime)

#     def update_content(self, _entity):
#         pass


# class Inventory(Location):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs, _height=1)
#         for x in range(INVENTORY_SIZE):
#             self.content[x] = None
#         self.selection = None

#     @property
#     def encumbrance(self):
#         return sum(i.encumbrance for n, i in self.content.items() if i)

#     def has_free_spot(self):
#         _spot = next((x for x in self.content if not self.content[x]), -1)
#         if _spot == -1:
#             return False
#         return True

#     def get(self, position):
#         if position in self.content:
#             return self.content[position]
#         return None

#     def free_position(self):
#         _spot = next((x for x in self.content if not self.content[x]), -1)
#         if _spot > -1:
#             return _spot
#         return None

#     def register(self, _entity):
#         """register content"""
#         if not _entity.id in self.entities:
#             self.entities[_entity.id] = _entity
#         x, y, z = _entity.position
#         self.content[x] = _entity

#     def unregister(self, _entity):
#         """register content"""
#         x, y, z = _entity.position
#         self.content[x] = None
#         if _entity.id in self.entities:
#             del self.entities[_entity.id]

#     def add(self, obj):
#         _spot = next((x for x in self.content if not self.content[x]), -1)
#         if _spot > -1:
#             obj.change_location((_spot, 0, 0), self)

#     def remove(self, obj):
#         self.unregister(obj)


# class Room(Location):
#     def __init__(self, name, world, _map):
#         super().__init__()
#         self.name = name
#         self.world = world

#         raw_map = [l for l in _map.split("\n") if l]
#         X = len(raw_map)
#         Y = max([len(l) for l in raw_map])
#         self.container = [[" " for _ in range(Y)] for _ in range(X)]
#         self.register_raw_map(raw_map)
#         self.map = self.map_from_entities()

#     @property
#     def characters(self):
#         return [ent for k, ent in self.entities.items() if isinstance(ent, character.Character)]

#     def get(self, position):
#         x, y, z = position
#         if x in self.content and y in self.content[x] and z in self.content[x][y]:
#             return self.content[x][y][z]
#         return None

#     def map_from_entities(self):
#         _map = copy.deepcopy(self.container)
#         for k, ent in self.entities.items():
#             for m, p in zip(ent.marker, ent.positions):
#                 x, y, z = p
#                 max_z = max([z for z in self.content[x][y]], default=-1)
#                 if z == max_z and self.content[x][y][z] is ent:
#                     _map[x][y] = (ent.color, m)
#         return _map

#     def layer_from_entities(self, _layer, debug=False):
#         _map = copy.deepcopy(self.container)
#         for k, ent in self.entities.items():
#             for m, p in zip(ent.marker, ent.positions):
#                 x, y, z = p
#                 if z == _layer and self.content[x][y][z] is ent:
#                     if debug:
#                         _map[x][y] = (ent.color, type(ent).__name__[0])
#                     else:
#                         _map[x][y] = (ent.color, m)
#         return _map

#     def on_update(self, _deltatime):
#         super().on_update(_deltatime)
#         # if self.redraw:
#         self.map = self.map_from_entities()

#     def update_content(self, _entity):
#         for x, y, z in _entity.last_positions:
#             if z in self.content[x][y] and self.content[x][y][z] is _entity:
#                 del self.content[x][y][z]
#         for x, y, z in _entity.positions:
#             self.content[x][y][z] = _entity
#         self.redraw = True

#     def register(self, _entity):
#         """register content"""
#         if not _entity.id in self.entities:
#             self.entities[_entity.id] = _entity
#             self.update_content(_entity)

#     def unregister(self, _entity):
#         """register content"""
#         for x, y, z in _entity.positions:
#             if z in self.content[x][y] and self.content[x][y][z] is _entity:
#                 del self.content[x][y][z]
#         if _entity.id in self.entities:
#             del self.entities[_entity.id]
#         self.redraw = True

#     def register_raw_map(self, raw_map):
#         for x in range(len(self.container)):
#             for y in range(len(self.container[x])):
#                 _marker = raw_map[x][y]
#                 if _marker != " ":
#                     # here it could be possible to add special characters for montesrs, items, etc...
#                     # or thin vs thick walls
#                     if _marker == "░":
#                         entity.Portal(_location=self, _position=(x, y, 0), _marker=_marker)
#                     elif _marker in "┘┐┌└┤┴┬├─│┼":
#                         entity.ThinWall(_location=self, _position=(x, y, 0), _marker=_marker)
#                     elif _marker in "═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬●■." or _marker.isalnum():
#                         entity.HardWall(_location=self, _position=(x, y, 0), _marker=_marker)
#                     else:
#                         entity.Empty(_location=self, _position=(x, y, 0), _marker=_marker)

#     def free_position(self, _entity):
#         _layer = _entity.layer
#         _extra_positions = _entity.extra_positions
#         pos = self.all_free_position(_layer, _extra_positions)
#         if pos:
#             return random.sample(pos, 1)[0]
#         return None

#     def all_free_position(self, _layer, _extra_positions):
#         _free = []
#         for x in range(len(self.container)):
#             for y in range(len(self.container[x])):
#                 _all = [(x + xp, y + yp, _layer + zp) for xp, yp, zp in [(0, 0, 0)] + _extra_positions]
#                 if all(self.is_empty((xp, yp, zp)) for xp, yp, zp in _all):
#                     _free.append((x, y, _layer))
#         return _free

#     def out_of_bounds(self, position):
#         x, y, z = position
#         return x < 0 or x >= len(self.container) or y < 0 or y >= len(self.container[x]) or z < 0 or z >= self.height

#     def is_empty(self, position):
#         x, y, z = position
#         if self.out_of_bounds(position):
#             return False
#         return not bool(self.get(position))
