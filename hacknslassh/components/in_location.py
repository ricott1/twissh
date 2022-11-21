from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING
from hacknslassh.components.image import Image
from hacknslassh.constants import Tile
from hacknslassh.gui.utils import RGBA_to_RGB, combine_RGB_colors, img_to_urwid_text, marker_to_urwid_text

from hacknslassh.utils import distance

if TYPE_CHECKING:
    from hacknslassh.dungeon import Dungeon
from hacknslassh.components.base import Component
import urwid
import pygame as pg


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class Markers(object):
    USER = {
        Direction.UP: "▲",
        Direction.DOWN: "▼",
        Direction.LEFT: "◀",
        Direction.RIGHT: "▶",
    }
    DOUBLE = {
        Direction.UP: "◢◣",
        Direction.DOWN: "◥◤",
        Direction.LEFT: "◀",
        Direction.RIGHT: "▶",
    }

class SightShape(Enum):
    CIRCLE = "circle"
    SQUARE = "square"
    CONE = "cone"

class SightShapeIcons(Enum):
    CIRCLE = "○"
    SQUARE = "□"
    CONE = "△"


@dataclass
class Sight(Component):
    _radius: int = 7
    color: tuple[int, int, int] = (105, 255, 204)
    shape: SightShape = SightShape.CIRCLE
    icon: SightShapeIcons = SightShapeIcons.CIRCLE
    MAX_RADIUS: int = 12

@dataclass
class InLocation(Component):
    """
    Component for entities that are in a dungeon.
    """

    dungeon: Dungeon
    _position: tuple[int, int, int] = (0, 0, 0)
    direction: Direction = Direction.UP
    marker: str = Markers.USER[Direction.UP]
    fg: tuple[int, int, int] = (255, 255, 255)
    bg: tuple[int, int, int] | None = None
    own_fg: tuple[int, int, int] = (125, 125, 225)
    visibility: int = 255
    _sight_radius: int = 6
    sight_fg = (105, 255, 204)
    MAX_SIGHT_RADIUS: int = 12
    
    def __post_init__(self):
        self.visited_tiles = set()
        self.visible_tiles = set()
        if self.sight_radius > 0:
            self.update_visible_and_visited_tiles()

    @property
    def position(self) -> tuple[int, int, int]:
        return self._position
    
    @position.setter
    def position(self, value: tuple[int, int, int]) -> None:
        self._position = value
        self.update_visible_and_visited_tiles()
    
    @property
    def sight_radius(self) -> int:
        return min(self.MAX_SIGHT_RADIUS, max(0, self._sight_radius))
    
    @sight_radius.setter
    def sight_radius(self, value: int) -> None:
        self._sight_radius = value
        self.update_visible_and_visited_tiles()

    @property
    def forward(self) -> tuple[int, int, int]:
        delta_x = int(self.direction == Direction.DOWN) - int(self.direction == Direction.UP)
        delta_y = int(self.direction == Direction.RIGHT) - int(self.direction == Direction.LEFT)
        x, y, z = self.position
        return (x + delta_x, y + delta_y, z)

    @property
    def above(self) -> tuple[int, int, int]:
        x, y, z = self.position
        return (x, y, z + 1)

    @property
    def below(self) -> tuple[int, int, int]:
        x, y, z = self.position
        return (x, y, z - 1)

    @property
    def floor(self) -> tuple[int, int, int]:
        x, y, z = self.position
        return (x, y, 0)

    @property
    def behind(self) -> tuple[int, int, int]:
        delta_x = int(self.direction == Direction.DOWN) - int(self.direction == Direction.UP)
        delta_y = int(self.direction == Direction.RIGHT) - int(self.direction == Direction.LEFT)
        x, y, z = self.position
        return (x - delta_x, y - delta_y, z)

    @property
    def right_side(self) -> tuple[int, int, int]:
        delta_x = int(self.direction == Direction.DOWN) - int(self.direction == Direction.UP)
        delta_y = int(self.direction == Direction.RIGHT) - int(self.direction == Direction.LEFT)
        x, y, z = self.position
        return (x - delta_y, y - delta_x, z)

    @property
    def left_side(self) -> tuple[int, int, int]:
        delta_x = int(self.direction == Direction.DOWN) - int(self.direction == Direction.UP)
        delta_y = int(self.direction == Direction.RIGHT) - int(self.direction == Direction.LEFT)
        x, y, z = self.position
        return (x + delta_y, y + delta_x, z)

    def update_visible_and_visited_tiles(self) -> None:
        x0, y0, _ = self.position
        max_visible_tiles = self.get_max_visible_tiles(x0, y0)
        self.visible_tiles = {(x, y) for x, y in max_visible_tiles if distance((x0, y0), (x, y)) <= self.sight_radius}
        self.visited_tiles |= self.visible_tiles
    

    def get_max_visible_tiles(self, x0: int, y0: int) -> set[tuple[int, int, int]]:
        # If shadows are cached, get them from cache
        if (x0, y0) in self.dungeon.shadow_cache:
            return self.dungeon.shadow_cache[(x0, y0)]

        # Otherwise calculate shadows for MAX_SIGHT_RADIUS and store in cache
        walls = [t for t in self.dungeon.wall_tiles if distance(t, (x0, y0)) <= self.MAX_SIGHT_RADIUS]
        max_visible_tiles = set()
        for x in range(x0 - self.MAX_SIGHT_RADIUS, x0 + self.MAX_SIGHT_RADIUS+1):
            for y in range(y0 - self.MAX_SIGHT_RADIUS, y0 + self.MAX_SIGHT_RADIUS+1):
                if distance((x0, y0), (x, y)) <= self.MAX_SIGHT_RADIUS:
                    if not is_tile_shadowed_by_walls((x0, y0), (x, y), walls):
                        max_visible_tiles.add((x, y))
        
        self.dungeon.shadow_cache[(x0, y0)] = max_visible_tiles
        return max_visible_tiles
        
        

    def rendered_map(self, camera_offset: tuple[int, int], screen_size: tuple[int, int]) -> list[list[str | tuple[urwid.AttrSpec, str]]]:
        max_y, max_x = screen_size
        # Double height since we are double buffering
        max_x *= 2
        off_y, off_x = camera_offset
        off_x //= 2
        rendered_map = [[Tile.EMPTY for _ in range(max_y)] for _ in range(max_x)]
        x0, y0, _ = self.position


        for x in range(0, max_x, 2):
            if x - off_x >= 2*len(self.dungeon.map):
                break
            if x < off_x:
                continue
            for y in range(max_y):
                if y - off_y >= len(self.dungeon.map[0]):
                    break
                if y < off_y:
                    continue
                
                if (x - off_x, y - off_y) not in self.visited_tiles and (x - off_x + 1, y - off_y) not in self.visited_tiles:
                    continue

                top_tile = self.dungeon.map[x - off_x][y - off_y]
                if len(self.dungeon.map) == x - off_x + 1:
                    btm_tile = Tile.EMPTY
                else:
                    btm_tile = self.dungeon.map[x - off_x + 1][y - off_y]

                if top_tile == Tile.EMPTY and btm_tile == Tile.EMPTY:
                    rendered_map[x//2][y] = Tile.EMPTY
                    continue

                top_d = distance((x - off_x, y - off_y), (x0, y0))
                top_a = max(55, 255 - int(200/self.sight_radius * top_d))
                top_marker, top_fg, _ = get_tile_info(top_tile)
                btm_d = distance((x - off_x + 1, y - off_y), (x0, y0))
                btm_a = max(55, 255 - int(200/self.sight_radius * btm_d))
                btm_marker, btm_fg, _ = get_tile_info(btm_tile)

                if top_d == 0:
                    top_fg = self.own_fg
                elif btm_d == 0:
                    btm_fg = self.own_fg
                else:
                    if (x - off_x, y - off_y) in self.visible_tiles:
                        top_fg = self.sight_fg
                    if (x - off_x + 1, y - off_y) in self.visible_tiles:
                        btm_fg = self.sight_fg

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

    def single_buffer_rendered_map(self, camera_offset: tuple[int, int], screen_size: tuple[int, int]) -> list[list[str | tuple[urwid.AttrSpec, str]]]:
        off_y, off_x = camera_offset
        max_y, max_x = screen_size
        rendered_map = [[Tile.EMPTY for _ in range(max_y)] for _ in range(max_x)]
        x0, y0, _ = self.position
 
        for x in range(max_x):
            if x - off_x >= len(self.dungeon.map):
                break
            if x < off_x:
                continue
            for y in range(max_y):
                if y - off_y >= len(self.dungeon.map[0]):
                    break
                if y < off_y:
                    continue

                if (x - off_x, y - off_y) not in self.visited_tiles: #in visited_tiles:
                    continue

                tile = self.dungeon.map[x - off_x][y - off_y]
                if tile is not Tile.EMPTY:
                    d = distance((x - off_x, y - off_y), (x0, y0))
                    a = max(55, 255 - int(200/self.sight_radius * d))
                    marker, fg, bg = get_tile_info(tile)

                    if d == 0:
                        marker, fg, bg = self.marker, self.own_fg, self.bg
                    elif (x - off_x, y - off_y) in self.visible_tiles:
                        fg = self.sight_fg
                        # a = 255 #debug
                
                    rendered_map[x][y] = marker_to_urwid_text(marker, fg, bg, a)
                        
                    
                        
        return rendered_map

def get_tile_info(tile: tuple[urwid.AttrSpec, str]) -> tuple[str, tuple[int, int, int], tuple[int, int, int] | None]:
    if tile is Tile.EMPTY:
        return Tile.EMPTY, (255, 255, 255), None
    marker = tile[1]
    rgb_values = tile[0].get_rgb_values()
    fg, bg = rgb_values[:3], rgb_values[3:]
    if fg == (None, None, None):
        fg = None
    if bg == (None, None, None):
        bg = None
    return marker, fg, bg

def is_tile_shadowed_by_walls(x_y0: tuple[int, int], x_y: tuple[int, int], walls: list[tuple[int, int]]) -> bool:
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

if __name__ == "__main__":
    def shadow_string(xs, ys, walls):
        if xs == x0 and ys == y0:
            return "O"
        if is_tile_shadowed_by_walls((x0, y0), (xs, ys), walls): 
            if (xs, ys) in walls: 
                return "S"
            return "s"
        if (xs, ys) in walls: 
            return "w"
        return "_"

    sight_radius = 8
    
    
    x0, y0 = (0, -1)
    walls = [(1, i) for i in range(-4, 9)] + [(-1, i) for i in range(-4, 9)]
    walls.append((2, 0))
    N = 10
    rendered_map = [["" for y in range(y0-sight_radius, y0+sight_radius+1)] for x in range(x0-sight_radius, x0+sight_radius+1)]
    
    for xs in range(x0-sight_radius, x0+sight_radius+1):
        for ys in range(y0-sight_radius, y0+sight_radius+1):
            rendered_map[xs][ys] = shadow_string(xs, ys, walls)
    print("\n")
    import sys
    for xs in range(x0-sight_radius, x0+sight_radius+1):
        for ys in range(y0-sight_radius, y0+sight_radius+1):
            sys.stdout.write(rendered_map[xs][ys])
        sys.stdout.write("\n")

    print("\n")



    
