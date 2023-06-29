from __future__ import annotations
import esper
from hacknslassh.components.sight import Sight
from hacknslassh.components.user import User
from hacknslassh.components.acting import Acting
from hacknslassh.components.utils import ParryCallback
from hacknslassh.processors.action import Action

from hacknslassh.components.in_location import InLocation
from hacknslassh.constants import *

class Parry(Action):
    name = "parry"
    recoil_cost = Recoil.MEDIUM
    description = "Parry"
    range = 1

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:

        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > Recoil.MAX - cls.recoil_cost:
            return
    
        if world.has_component(ent_id, ParryCallback):
            return
        
        
        world.add_component(ent_id, ParryCallback.new(world, ent_id, cls.recoil_cost))

        acting.action_recoil += cls.recoil_cost
        
        if user := world.try_component(ent_id, User):
            user.mind.process_event("player_acting_changed")
        in_location = world.component_for_entity(ent_id, InLocation)
        for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
            if other_ent_id != ent_id and other_in_loc.dungeon == in_location.dungeon and in_location.position in other_sight.visible_tiles:
                other_user.mind.process_event("redraw_ui")
    