from __future__ import annotations
import esper
from hacknslassh.components.characteristics import RGB
from hacknslassh.components.sight import Sight
from hacknslassh.components.user import User
from hacknslassh.processors.action import Action
from hacknslassh.utils import distance

from ..components.in_location import Direction, InLocation, Markers
from hacknslassh.constants import *

class Move(Action):
    name = "move"
    recoil_cost = Recoil.MINIMUM
    description = "Move forward"
    direction = None

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        from ..components import Acting
        in_location = world.component_for_entity(ent_id, InLocation)
        direction = in_location.direction
        if direction != cls.direction:
            in_location.direction = cls.direction
            in_location.marker = Markers.USER[cls.direction]
            in_location.dungeon.set_renderable_entity(ent_id)
            if user := world.try_component(ent_id, User):
                user.mind.process_event("redraw_local_ui")
                user.mind.process_event("player_status_changed")
        else:
            acting = world.try_component(ent_id, Acting)
            if not acting or acting.movement_recoil > 0:
                return
            target_is_free = in_location.dungeon.get_at(in_location.forward) is None
            if not target_is_free:
                return
            x, y, z = in_location.position
            new_x = x + int(direction == Direction.DOWN) - int(direction == Direction.UP)
            new_y = y + int(direction == Direction.RIGHT) - int(direction == Direction.LEFT)
            new_position = (new_x, new_y, z)
            if in_location.dungeon.is_in_bound(new_position):
                in_location.dungeon.remove_renderable_entity(ent_id)
                in_location.position = new_position
                in_location.dungeon.set_renderable_entity(ent_id)
                dex = world.component_for_entity(ent_id, RGB).dexterity
                acting.movement_recoil = cls.recoil_cost * (25 / (10 + dex))
                 
                if user := world.try_component(ent_id, User):
                    user.mind.process_event("player_movement")

        sight = world.component_for_entity(ent_id, Sight)
        x0, y0, _ = in_location.position
        sight.update_visible_and_visited_tiles((x0, y0), in_location.direction, in_location.dungeon)
        
        if user := world.try_component(ent_id, User):
            user.mind.process_event("redraw_local_ui")
            user.mind.process_event("player_sight_changed")
        for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
            if other_ent_id != ent_id and other_in_loc.dungeon == in_location.dungeon and distance(in_location.position, other_in_loc.position) <= other_sight.radius:
                other_user.mind.process_event("redraw_local_ui")
    
    

class MoveUp(Move):
    name = "move_up"
    description = "Move up"
    direction = "up"

class MoveDown(Move):
    name = "move_down"
    description = "Move down"
    direction = "down"


class MoveLeft(Move):
    name = "move_left"
    description = "Move left"
    direction = "left"


class MoveRight(Move):
    name = "move_right"
    description = "Move right"
    direction = "right"