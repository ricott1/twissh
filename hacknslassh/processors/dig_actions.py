from __future__ import annotations
import esper
from hacknslassh.components.sight import MAX_SIGHT_RADIUS, Sight
from hacknslassh.components.user import User
from hacknslassh.components.acting import Acting
from hacknslassh.processors.action import Action
from hacknslassh.utils import distance

from ..components.in_location import Direction, InLocation
from hacknslassh.constants import *

class Dig(Action):
    name = "dig"
    recoil_cost = Recoil.SHORT
    description = "Dig a wall"
    direction = None

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        
        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > 0:
            return
        
        in_location = world.component_for_entity(ent_id, InLocation)
        dungeon = in_location.dungeon
        if not dungeon.is_wall_at(in_location.forward):
            return

        if not dungeon.is_in_bound(in_location.forward):
            return

        acting.action_recoil = cls.recoil_cost
        
        dungeon.destroy_wall_at(in_location.forward)
        x0, y0, _ = in_location.forward
        if in_location.direction == Direction.UP:
            target_positions = [(x0 - 1, y0, 1), (x0 - 1, y0 - 1, 1), (x0 - 1, y0 + 1, 1), (x0, y0 - 1, 1), (x0, y0 + 1, 1)]
        elif in_location.direction == Direction.RIGHT:
            target_positions = [(x0, y0 + 1, 1), (x0 - 1, y0 + 1, 1), (x0 + 1, y0 + 1, 1), (x0 - 1, y0, 1), (x0 + 1, y0, 1)]
        elif in_location.direction == Direction.DOWN:
            target_positions = [(x0 + 1, y0, 1), (x0 + 1, y0 - 1, 1), (x0 + 1, y0 + 1, 1), (x0, y0 - 1, 1), (x0, y0 + 1, 1)]
        elif in_location.direction == Direction.LEFT:
            target_positions = [(x0, y0 - 1, 1), (x0 - 1, y0 - 1, 1), (x0 + 1, y0 - 1, 1), (x0 - 1, y0, 1), (x0 + 1, y0, 1)]
    
        for pos in target_positions:
            if dungeon.is_empty_at(pos):
                dungeon.create_wall_at(pos)
                dungeon.set_renderable_entity(world.create_entity(InLocation(dungeon, pos, marker=Tile.WALL)))
                
        # Delete dungeon shadow cache since it could have been changed buy the dig.
        for x in range(x0 - MAX_SIGHT_RADIUS, x0 + MAX_SIGHT_RADIUS + 1):
            for y in range(y0 - MAX_SIGHT_RADIUS, y0 + MAX_SIGHT_RADIUS + 1):
                if distance((x0, y0), (x, y)) <= MAX_SIGHT_RADIUS:
                    if (x, y) in dungeon.shadow_cache:
                        del dungeon.shadow_cache[(x, y)]
            
        if user := world.try_component(ent_id, User):
                user.mind.process_event("redraw_ui")
                user.mind.process_event("player_acting_changed")
        for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
            if other_ent_id != ent_id and other_in_loc.dungeon == in_location.dungeon and in_location.position in other_sight.visible_tiles:
                other_user.mind.process_event("redraw_ui")
    