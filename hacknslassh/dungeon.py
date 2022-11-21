from __future__ import annotations
from hacknslassh.constants import Tile
from hacknslassh.gui.utils import marker_to_urwid_text
from hacknslassh.utils import nested_dict
from .components import InLocation
import urwid
import esper
import random
import itertools
import sys


"""COORDINATES:
    |    y
   - ---->
    |
    |
    |
    v x
"""

class Cell(object):
    def __init__(self, x: int, y: int, id: int) -> None:
        self.x = x
        self.y = y
        self.id = id
        self.connected = False
        self.connected_to: list[Cell] = []
        self.floor_tiles: list[tuple[int, int]] = []

    def connect(self, other: Cell) -> None:
        self.connected_to.append(other)
        other.connected_to.append(self)
        self.connected = True
        other.connected = True

    def __str__(self) -> str:
        return "(%i,%i)" % (self.x, self.y)
    

class Dungeon(object):
    def __init__(self, world: esper.World, max_z: int = 5, cells_x: int = 4, cells_y: int = 5, cell_size: int = 24) -> None:
        self.world = world
        self.max_z = max_z
        self.content = nested_dict()
        #stores cache of shadowed tiles at a certain position for quick access, to be used in inlocation.update_visited_and_visible_tiles
        self.shadow_cache: dict[tuple[int, int], set] = {} 
        self.urwid_text: list[tuple[urwid.AttrSpec, str] | str] = []

        self.max_x, self.max_y, self.tiles = generate_dungeon(cells_x, cells_y, cell_size)
        self.map = [[Tile.EMPTY for _ in range(self.max_y)] for _ in range(self.max_x)]
        self.empty_map = [[Tile.EMPTY for _ in range(self.max_y)] for _ in range(self.max_x)]

        self.floor_tiles = [pos for pos, tile in self.tiles.items() if tile == Tile.FLOOR]
        self.wall_tiles = [pos for pos, tile in self.tiles.items() if tile == Tile.WALL]

        for tile in self.wall_tiles:
            self.set_renderable_entity(self.world.create_entity(InLocation(self, (tile[0], tile[1], 1), marker=Tile.WALL, _sight_radius=0)))
            self.empty_map[tile[0]][tile[1]] = marker_to_urwid_text(Tile.WALL, (255, 255, 255), None, 255)
        for tile in self.floor_tiles:
            self.map[tile[0]][tile[1]] = marker_to_urwid_text(Tile.FLOOR, (255, 255, 255), None, 255)
            self.empty_map[tile[0]][tile[1]] = marker_to_urwid_text(Tile.FLOOR, (255, 255, 255), None, 255)

    def random_floor_tile(self) -> tuple[int, int]:
        return random.choice(self.floor_tiles)
        
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
    
    def is_wall_at(self, position: tuple) -> bool:
        x, y, z = position
        if x in self.content and y in self.content[x] and z in self.content[x][y]:
            return self.world.component_for_entity(self.content[x][y][z], InLocation).marker == Tile.WALL
        return False
    
    def get_at(self, position: tuple) -> int | None:
        x, y, z = position
        if not self.is_in_bound(position):
            return None
        if x in self.content and y in self.content[x] and z in self.content[x][y]:
            return self.content[x][y][z]
        return None
    
    def set_at(self, position: tuple, ent_id: int) -> None:
        if not self.is_in_bound(position):
            return
        x, y, z = position
        if x not in self.content:
            self.content[x] = nested_dict()
        if y not in self.content[x]:
            self.content[x][y] = nested_dict()
        self.content[x][y][z] = ent_id

    def remove_at(self, position: tuple) -> None:
        x, y, z = position
        if x in self.content and y in self.content[x] and z in self.content[x][y]:
            del self.content[x][y][z]
    
    def set_renderable_entity(self, ent_id: int) -> None:
        in_location = self.world.component_for_entity(ent_id, InLocation)
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

    def remove_renderable_entity(self, ent_id: int) -> None:
        in_location = self.world.component_for_entity(ent_id, InLocation)
        position = in_location.position
        x, y, z = position
        if x in self.content and y in self.content[x] and z in self.content[x][y]:
            del self.content[x][y][z]
            if self.max_z_at(position) >= 0:
                top = self.world.component_for_entity(self.get_top_at(position), InLocation)
                self.map[x][y] = marker_to_urwid_text(top.marker, top.fg, top.bg, top.visibility)
            else:
                self.map[x][y] = self.empty_map[x][y]


    

def _AStar(start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
    def heuristic(a: tuple[int, int], b: tuple[int, int]) -> float:
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    def reconstruct_path(n: tuple[int, int]) -> list[tuple[int, int]]:
        if n == start:
            return [n]
        return reconstruct_path(came_from[n]) + [n]

    def neighbors(n: tuple[int, int]) -> tuple[tuple[int, int]]:
        x, y = n
        return (x - 1, y), \
          (x + 1, y), \
          (x, y - 1), \
          (x, y + 1)

    closed = set()
    open = set()
    open.add(start)
    came_from = {}
    gScore = {start: 0}
    fScore = {start: heuristic(start, goal)}

    while open:
        current = None
        for i in open:
            if current is None or fScore[i] < fScore[current]:
                current = i

        if current == goal:
            return reconstruct_path(goal)

        open.remove(current)
        closed.add(current)

        for neighbor in neighbors(current):
            if neighbor in closed:
                continue
            g = gScore[current] + 1

            if neighbor not in open or g < gScore[neighbor]:
                came_from[neighbor] = current
                gScore[neighbor] = g
                fScore[neighbor] = gScore[neighbor] + heuristic(neighbor, goal)
                if neighbor not in open:
                    open.add(neighbor)
    return []


def generate_dungeon(cells_x: int, cells_y: int, cell_size: int=6) -> tuple[int, int, dict[tuple[int, int], Tile]]:
    # 1. Divide the map into a grid of evenly sized cells.
    cells: dict[tuple[int, int], Cell] = {}
    for y in range(cells_y):
        for x in range(cells_x):
            c = Cell(x, y, len(cells))
            cells[(c.x, c.y)] = c

    # 2. Pick a random cell as the current cell and mark it as connected.
    current = last_cell = first_cell = random.choice(list(cells.values()))
    current.connected = True

    # 3. While the current cell has unconnected neighbor cells:
    def get_neighbor_cells(cell):
        for x, y in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            try:
                yield cells[(cell.x + x, cell.y + y)]
            except KeyError:
                continue

    while True:
        unconnected = list(filter(lambda x: not x.connected, get_neighbor_cells(current)))
        if not unconnected:
            break

        # 3a. Connect to one of them.
        neighbor = random.choice(unconnected)
        current.connect(neighbor)

        # 3b. Make that cell the current cell.
        current = last_cell = neighbor

    # 4. While there are unconnected cells:
    while True:
        unconnected = list(filter(lambda x: not x.connected, cells.values()))
        if not unconnected:
            break

        # 4a. Pick a random connected cell with unconnected neighbors and connect to one of them.
        candidates: tuple[Cell, list[Cell]] = []
        for cell in filter(lambda x: x.connected, cells.values()):
            neighbors = list(filter(lambda x: not x.connected, get_neighbor_cells(cell)))
            if not neighbors:
                continue
            candidates.append((cell, neighbors))
        if candidates:
            n_connections = random.randint(1, len(candidates))
            connections = random.sample(candidates, n_connections)
            for cell, neighbors in connections:
                cell.connect(random.choice(neighbors))

    # 5. Pick 0 or more pairs of adjacent cells that are not connected and connect them.
    extraConnections = random.randint(int((cells_x + cells_y) / 4), int((cells_x + cells_y) / 1.2))
    maxRetries = 10
    while extraConnections > 0 and maxRetries > 0:
        cell = random.choice(list(cells.values()))
        neighbor = random.choice(list(get_neighbor_cells(cell)))
        if cell in neighbor.connected_to:
            maxRetries -= 1
            continue
        cell.connect(neighbor)
        extraConnections -= 1

    # 6. Within each cell, create a room of random shape
    cell_size = max(6, cell_size)
    rooms = []
    for cell in cells.values():
        width = random.randint(4, cell_size - 2)
        height = random.randint(4, cell_size - 2)
        x = (cell.x * cell_size) + random.randint(1, cell_size - width - 1)
        if x % 2 == 0:
            x += 1
        if x < 2:
            x = 2
        width = (width //2) * 2
        y = (cell.y * cell_size) + random.randint(1, cell_size - height - 1)
        # y = 4
        floor_tiles = []
        for i in range(width):
            for j in range(height):
                floor_tiles.append((x + i, y + j))
        cell.floor_tiles = floor_tiles
        rooms.append(floor_tiles)

    # 7. For each connection between two cells:
    corridors = []
    connections: dict[tuple[int, int], tuple[list[tuple[int, int]], list[tuple[int, int]]]] = {}
    for c in cells.values():
        for other in c.connected_to:
            connections[tuple(sorted((c.id, other.id)))] = (c.floor_tiles, other.floor_tiles)
    for a, b in connections.values():
        # 7a. Create a random corridor between the rooms in each cell.
        start: tuple[int, int] = random.choice(a)
        end: tuple[int, int] = random.choice(b)

        corridor = []
        for tile in _AStar(start, end):
            if tile not in a and tile not in b:
                corridor.append(tile)
                corridor.append((tile[0] + 1, tile[1]))
                corridor.append((tile[0], tile[1] + 1))
        rooms.append(corridor)

    # 8. Place staircases in the cell picked in step 2 and the lest cell visited in step 3b.
    # stairs_up = random.choice(first_cell.floor_tiles)
    # stairs_down = random.choice(last_cell.floor_tiles)

    # create tiles
    tiles = {}
    tiles_x = cells_x * cell_size
    tiles_y = cells_y * cell_size
    for x in range(tiles_x):
        for y in range(tiles_y):
            tiles[(x, y)] = Tile.EMPTY
    for xy in itertools.chain.from_iterable(rooms):
        tiles[xy] = Tile.FLOOR

    # every tile adjacent to a floor is a wall
    def get_neighbor_tiles(xy):
        tx, ty = xy
        for x, y in ((-1, -1), (0, -1), (1, -1),
                     (-1, 0), (1, 0),
                     (-1, 1), (0, 1), (1, 1)):
            try:
                yield tiles[(tx + x, ty + y)]
            except KeyError:
                continue

    for xy, tile in tiles.items():
        if not tile == Tile.FLOOR and Tile.FLOOR in get_neighbor_tiles(xy):
            tiles[xy] = Tile.WALL
    # tiles[stairs_up] = Tile.STAIRS_UP
    # tiles[stairs_down] = Tile.STAIRS_DOWN

    # Set corridors to empty tiles
    for corridor in corridors:
        for xy in corridor:
            tiles[xy] = Tile.EMPTY

    return (tiles_x, tiles_y, tiles)


if __name__ == "__main__":
    dungeon = generate_dungeon(6, 3, 20)
    for y in range(dungeon.tiles_y):
        for x in range(dungeon.tiles_x):
            sys.stdout.write(dungeon.tiles[(x, y)])
        sys.stdout.write("\n")
