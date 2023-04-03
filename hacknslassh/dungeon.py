from __future__ import annotations
from hacknslassh.constants import Tile, MIN_ALPHA
from hacknslassh.color_utils import Color
from hacknslassh.gui.utils import RGBA_to_RGB, marker_to_urwid_text
from hacknslassh.utils import distance, nested_dict
from .components import InLocation, MAX_SIGHT_RADIUS, Sight
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
    def __init__(self, world: esper.World, max_z: int = 5) -> None:
        self.world = world
        self.max_z = max_z
        self.content = nested_dict()
        #stores cache of shadowed tiles at a certain position for quick access, to be used in inlocation.update_visited_and_visible_tiles
        self.shadow_cache: dict[tuple[int, int], list[int, int, float]] = {} 
        self.visible_cache: dict[tuple[int, int], list[int, int, float]] = {} 
        self.urwid_text: list[tuple[urwid.AttrSpec, str] | str] = []

        self.max_x, self.max_y, self.tiles = generate_dungeon(compactness=2)
        self.map = [[Tile.EMPTY for _ in range(self.max_y + 1)] for _ in range(self.max_x + 1)]
        # self.empty_map = [[Tile.EMPTY for _ in range(self.max_y)] for _ in range(self.max_x)]

        self.floor_tiles = [pos for pos, tile in self.tiles.items() if tile == Tile.FLOOR]
        self.wall_tiles = [pos for pos, tile in self.tiles.items() if tile == Tile.WALL]

        for tile in self.wall_tiles:
            self.set_renderable_entity(self.world.create_entity(InLocation(self, (tile[0], tile[1], 1), marker=Tile.WALL)))
            # self.empty_map[tile[0]][tile[1]] = marker_to_urwid_text(Tile.WALL, Color.WHITE, None, 255)
        for tile in self.floor_tiles:
            self.map[tile[0]][tile[1]] = marker_to_urwid_text(Tile.FLOOR, Color.WHITE, None, 255)
            # self.empty_map[tile[0]][tile[1]] = marker_to_urwid_text(Tile.FLOOR, Color.WHITE, None, 255)

    def random_floor_tile(self) -> tuple[int, int]:
        return random.choice(self.floor_tiles)
    
    def random_free_floor_tile(self) -> tuple[int, int]:
        return random.choice([t for t in self.floor_tiles if not self.get_at((*t, 1))])
    
    def destroy_wall_at(self, position: tuple[int, int, int]) -> None:
        wall_id = self.get_at(position)
        if not wall_id or not self.is_wall_at(position):
            return
        
        x, y, _ = position
        self.remove_renderable_entity(wall_id)
        self.world.delete_entity(wall_id)
        self.wall_tiles.remove((x, y))
        self.floor_tiles.append((x, y))

    def create_wall_at(self, position: tuple[int, int, int]) -> None:
        if not self.is_wall_at(position):
            self.set_renderable_entity(self.world.create_entity(InLocation(self, position, marker=Tile.WALL)))
            x, y, _ = position
            if (x, y) in self.floor_tiles:
                self.floor_tiles.remove((x, y))
            self.wall_tiles.append((x, y))

    def non_shadowed_tiles_at(self, x0: int, y0: int) -> list[tuple[int, int, float]]:
        # If shadows are cached, get them from cache
        if (x0, y0) in self.shadow_cache:
            return self.shadow_cache[(x0, y0)]

        # Otherwise calculate shadows for MAX_SIGHT_RADIUS and store in cache
        walls = [t for t in self.wall_tiles if distance(t, (x0, y0)) <= MAX_SIGHT_RADIUS]
        max_visible_tiles = []
        for x, y, d in self.visible_tiles_at(x0, y0):
            if not is_tile_shadowed_by_walls((x0, y0), (x, y), walls):
                max_visible_tiles.append((x, y, d))
        
        self.shadow_cache[(x0, y0)] = sorted(max_visible_tiles, key=lambda t: t[2])
        return self.shadow_cache[(x0, y0)]
    
    def visible_tiles_at(self, x0: int, y0: int) -> list[tuple[int, int, float]]:
        # If shadows are cached, get them from cache
        if (x0, y0) in self.visible_cache:
            return self.visible_cache[(x0, y0)]

        # Otherwise calculate shadows for MAX_SIGHT_RADIUS and store in cache
        max_visible_tiles = []
        for x in range(x0 - MAX_SIGHT_RADIUS, x0 + MAX_SIGHT_RADIUS+1):
            for y in range(y0 - MAX_SIGHT_RADIUS, y0 + MAX_SIGHT_RADIUS+1):
                if (d := distance((x0, y0), (x, y))) <= MAX_SIGHT_RADIUS:
                    max_visible_tiles.append((x, y, d))
        
        self.visible_cache[(x0, y0)] = sorted(max_visible_tiles, key=lambda t: t[2])
        return self.visible_cache[(x0, y0)]
        
    def is_in_bound(self, position: tuple[int, int, int]) -> bool:
        x, y, z = position
        return x < self.max_x and y < self.max_y and z < self.max_z and x >= 0 and y >= 0 and z >= 0

    def max_z_at(self, position: tuple[int, int, int]) -> int:
        x, y, _ = position
        if x in self.content and y in self.content[x]:
            return max([z for z in self.content[x][y]], default=-1)
        return -1
    
    def get_top_at(self, position: tuple[int, int, int]) -> int:
        z = self.max_z_at(position)
        if z >= 0:
            x, y, _ = position
            return self.content[x][y][z]
        return 0
    
    def is_wall_at(self, position: tuple[int, int, int]) -> bool:
        x, y, _ = position
        return (x, y) in self.wall_tiles
    
    def is_empty_at(self, position: tuple[int, int, int]) -> bool:
        x, y, _ = position
        return self.is_in_bound(position) and self.map[x][y] == Tile.EMPTY

    def get_at(self, position: tuple[int, int, int]) -> int | None:
        x, y, z = position
        if not self.is_in_bound(position):
            return None
        if x in self.content and y in self.content[x] and z in self.content[x][y]:
            return self.content[x][y][z]
        return None
    
    def set_at(self, position: tuple[int, int, int], ent_id: int) -> None:
        if not self.is_in_bound(position):
            return
        x, y, z = position
        if x not in self.content:
            self.content[x] = nested_dict()
        if y not in self.content[x]:
            self.content[x][y] = nested_dict()
        self.content[x][y][z] = ent_id

    def remove_at(self, position: tuple[int, int, int]) -> None:
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
                self.map[x][y] = marker_to_urwid_text(Tile.FLOOR, Color.WHITE, None, 255)

    def remove_renderable_entity_at(self, position: tuple[int, int, int]) -> None:
        ent_id = self.get_at(position)
        if ent_id is not None:
            self.remove_renderable_entity(ent_id)


minimap_reduction = 2

def render_dungeon_map(in_loc: InLocation, sight: Sight, camera_offset: tuple[int, int], screen_size: tuple[int, int], double_buffer: bool = True) -> list[list[str | tuple[urwid.AttrSpec, str]]]:
    if double_buffer:
        return render_map_double_buffer(in_loc, sight, camera_offset, screen_size)
    else:
        return render_map_single_buffer(in_loc, sight, camera_offset, screen_size)

def render_map_single_buffer(in_loc: InLocation, sight: Sight, camera_offset: tuple[int, int], screen_size: tuple[int, int]) -> list[list[str | tuple[urwid.AttrSpec, str]]]:
    max_y, max_x = screen_size
    off_y, off_x = camera_offset
    rendered_map = [[Tile.EMPTY for _ in range(max_y)] for _ in range(max_x)]
    x0, y0, _ = in_loc.position

    for x in range(max_x):
        if x - off_x >= len(in_loc.dungeon.map):
            break
        if x < off_x:
            continue
        for y in range(max_y):
            if y - off_y >= len(in_loc.dungeon.map[0]):
                break
            if y < off_y:
                continue

            if (x - off_x, y - off_y) not in sight.visited_tiles:
                continue

            tile = in_loc.dungeon.map[x - off_x][y - off_y]
            if tile == Tile.EMPTY:
                continue
            d = distance((x - off_x, y - off_y), (x0, y0))
            a = MIN_ALPHA
            marker, fg, bg = get_tile_info(tile)

            if d == 0:
                marker, fg, bg = in_loc.marker, in_loc.own_fg, in_loc.bg
                a = 255
            elif (x - off_x, y - off_y) in sight.visible_tiles:
                a = max(MIN_ALPHA, 255 - int((255-MIN_ALPHA)/sight.radius * d))
            elif marker not in (Tile.WALL, Tile.FLOOR):
                marker = Tile.FLOOR
        
            rendered_map[x][y] = marker_to_urwid_text(marker, fg, bg, a)
                
    return rendered_map

def render_map_double_buffer(in_loc: InLocation, sight: Sight, camera_offset: tuple[int, int], screen_size: tuple[int, int]) -> list[list[str | tuple[urwid.AttrSpec, str]]]:
    max_y, max_x = screen_size
    # Double height since we are double buffering
    max_x *= 2
    off_y, off_x = camera_offset
    rendered_map = [[Tile.EMPTY for _ in range(max_y)] for _ in range(max_x)]
    x0, y0, _ = in_loc.position

    for x in range(0, max_x, 2):
        if x - off_x >= len(in_loc.dungeon.map):
            break
        if x < off_x:
            continue
        for y in range(max_y):
            if y - off_y >= len(in_loc.dungeon.map[0]):
                break
            if y < off_y:
                continue
            
            if (x - off_x, y - off_y) not in sight.visited_tiles and (x - off_x + 1, y - off_y) not in sight.visited_tiles:
                continue

            top_tile = in_loc.dungeon.map[x - off_x][y - off_y]
            if len(in_loc.dungeon.map) == x - off_x + 1:
                btm_tile = Tile.EMPTY
            else:
                btm_tile = in_loc.dungeon.map[x - off_x + 1][y - off_y]

            if top_tile == Tile.EMPTY and btm_tile == Tile.EMPTY:
                continue

            top_d = distance((x - off_x, y - off_y), (x0, y0))
            top_marker, top_fg, _ = get_tile_info(top_tile)
            btm_d = distance((x - off_x + 1, y - off_y), (x0, y0))             
            btm_marker, btm_fg, _ = get_tile_info(btm_tile)
            top_a = MIN_ALPHA
            btm_a = MIN_ALPHA

            if top_d == 0:
                top_fg = in_loc.own_fg
                top_a = 255
            elif btm_d == 0:
                btm_fg = in_loc.own_fg
                btm_a = 255
            else:
                if (x - off_x, y - off_y) in sight.visible_tiles:
                    top_a = max(MIN_ALPHA, 255 - int((255-MIN_ALPHA)/sight.radius * top_d))
                    # top_fg = sight.color
                elif top_marker not in (Tile.WALL, Tile.FLOOR):
                    top_marker = Tile.FLOOR
                if (x - off_x + 1, y - off_y) in sight.visible_tiles:
                    btm_a = max(MIN_ALPHA, 255 - int((255-MIN_ALPHA)/sight.radius * btm_d))
                    # btm_fg = sight.color
                elif btm_marker not in (Tile.WALL, Tile.FLOOR):
                    btm_marker = Tile.FLOOR
                
            top_r, top_g, top_b = RGBA_to_RGB(*top_fg, top_a)
            top_attr = f"#{top_r:02x}{top_g:02x}{top_b:02x}"
            btm_r, btm_g, btm_b = RGBA_to_RGB(*btm_fg, btm_a)
            btm_attr = f"#{btm_r:02x}{btm_g:02x}{btm_b:02x}"

            # Two floor tiles are rendered together as a single floor tile
            # Assumption: Tile.FLOOR and Tile.EMPTY can not be adjacent
            if top_marker == btm_marker == Tile.FLOOR:
                if top_d < btm_d:
                    rendered_map[x//2][y] = (urwid.AttrSpec(top_attr, ""), top_marker)
                else:
                    rendered_map[x//2][y] = (urwid.AttrSpec(btm_attr, ""), btm_marker)   
            # else both will be rendered
            elif top_marker not in (Tile.EMPTY, Tile.FLOOR) and btm_marker in (Tile.EMPTY, Tile.FLOOR):
                rendered_map[x//2][y] = (urwid.AttrSpec(top_attr, ""), "▀")
            elif top_marker in (Tile.EMPTY, Tile.FLOOR) and btm_marker not in (Tile.EMPTY, Tile.FLOOR):
                rendered_map[x//2][y] = (urwid.AttrSpec(btm_attr, ""), "▄")
            else:
                rendered_map[x//2][y] = (urwid.AttrSpec(btm_attr, top_attr), "▄")
    
    return rendered_map

def render_dungeon_minimap(in_loc: InLocation, sight: Sight) -> list[list[str | tuple[urwid.AttrSpec, str]]]:
    cf = minimap_reduction
    max_y, max_x = (len(in_loc.dungeon.map[0]), len(in_loc.dungeon.map))
    rendered_map = [[Tile.EMPTY for _ in range((max_y//cf)+1)] for _ in range((max_x//(2*cf))+1)]
    x0, y0, _ = in_loc.position 

    for x in range(0, max_x, 2*cf):
        for y in range(0, max_y, cf):
            top_range = [(x + j, y + i) for j in range(cf) for i in range(cf)]
            btm_range = [(x + cf + j, y + i) for j in range(cf) for i in range(cf)]

            visited_top = any([(tile in sight.visited_tiles) and (tile in in_loc.dungeon.floor_tiles) for tile in top_range])
            visited_btm = any([(tile in sight.visited_tiles) and (tile in in_loc.dungeon.floor_tiles) for tile in btm_range])

            if not visited_top and not visited_btm:
                continue

            top_attr = f"#ffffff"
            btm_attr = f"#ffffff"
            if (x0, y0) in top_range:
                r, g, b = sight.color
                top_attr = f"#{r:02x}{g:02x}{b:02x}" 
            elif (x0, y0) in btm_range:
                r, g, b = sight.color
                btm_attr = f"#{r:02x}{g:02x}{b:02x}" 

            if visited_top and not visited_btm:
                rendered_map[x//(2*cf)][y//cf] = (urwid.AttrSpec(top_attr, ""), "▀")
            elif not visited_top and visited_btm:
                rendered_map[x//(2*cf)][y//cf] = (urwid.AttrSpec(btm_attr, ""), "▄")
            elif visited_top and visited_btm:
                rendered_map[x//(2*cf)][y//cf] = (urwid.AttrSpec(btm_attr, top_attr), "▄")
    
    return rendered_map



def get_tile_info(tile: tuple[urwid.AttrSpec, str]) -> tuple[str, tuple[int, int, int], tuple[int, int, int] | None]:
    if tile is Tile.EMPTY:
        return Tile.EMPTY, Color.WHITE, None
    marker = tile[1]
    rgb_values = tile[0].get_rgb_values()
    fg, bg = rgb_values[:3], rgb_values[3:]
    if fg == (None, None, None):
        fg = None
    if bg == (None, None, None):
        bg = None
    return marker, fg, bg


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

def is_tile_shadowed_by_walls(x_y0: tuple[int, int], x_y: tuple[int, int], walls: list[tuple[int, int]]) -> bool:
    #FIXME: for the love of god i don't know why it doesnt work
    if x_y == x_y0:
        return False
    x0, y0 = x_y0
    x, y = x_y
    if x0 == x:
        for yi in range(min(y0, y) + 1, max(y0, y)):
            if (x, yi) in walls:
                return True
        return False
    
    # if y0 == y:
    #     for xi in range(min(x0, x) + 1, max(x0, x)):
    #         if (xi, y) in walls:
    #             return True
    #     return False

    m = (y0 - y) / (x0 - x)
    for xi in range(min(x0, x) + 1, max(x0, x)):
        yi = int(m * (xi - x0) + y0)
        if (xi, yi) in walls:
            return True

    for yi in range(min(y0, y) + 1, max(y0, y)):
        xi = int((yi - y0) / m + x0)
        if (xi, yi) in walls:
            return True

    return False

def generate_dungeon(compactness = 0) -> tuple[int, int, dict[tuple[int, int], Tile]]:
    cell_size = 7 + (4 + random.randint(-1, 1)) * compactness
    extraConnections = 3 * compactness - random.randint(compactness, 2*compactness)
    ISOLATE_ROOM_PROB = max(0, 0.1 - 0.01 * compactness)

    cells_y = (28*minimap_reduction)//cell_size #to fit horizontally into the minimap width
    cells_x = (38*minimap_reduction)//cell_size #to fit vertically into the minimap height

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
    while unconnected := list(filter(lambda x: not x.connected, cells.values())):
        # unconnected = list(filter(lambda x: not x.connected, cells.values()))
        # if not unconnected:
        #     break

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
        # Isolate a room with a small probability.
        if random.random() < ISOLATE_ROOM_PROB:
            continue
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

    # 8. Place staircases in the cell picked in step 2 and the last cell visited in step 3b.
    stairs_up = random.choice(first_cell.floor_tiles)
    stairs_down = random.choice(last_cell.floor_tiles)

    # create tiles
    tiles = {}
    max_x = cells_x * cell_size
    max_y = cells_y * cell_size
    
    for x in range(max_x):
        for y in range(max_y):
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

    return (max_x, max_y, tiles)


if __name__ == "__main__":
    dungeon = generate_dungeon()
    for y in range(dungeon.tiles_y):
        for x in range(dungeon.tiles_x):
            sys.stdout.write(dungeon.tiles[(x, y)])
        sys.stdout.write("\n")
