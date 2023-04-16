from __future__ import annotations
import esper
from hacknslassh.components.description import ActorInfo
from hacknslassh.components.sight import Sight
from hacknslassh.components.tokens import CatchableToken
from hacknslassh.components.user import User
from hacknslassh.components.acting import Acting
from hacknslassh.processors.action import Action

from ..components.in_location import InLocation
from hacknslassh.constants import *

class Catch(Action):
    name = "catch"
    recoil_cost = Recoil.LONG
    description = "Catch'm'all"
    direction = None

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        
        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > 0:
            return
        
        in_location = world.component_for_entity(ent_id, InLocation)
        dungeon = in_location.dungeon
        target = dungeon.get_at(in_location.forward)
        if not target or not world.try_component(target, CatchableToken):
            return

        acting.action_recoil = cls.recoil_cost
        #FIXME: add catch logic

        in_location.dungeon.remove_renderable_entity_at(in_location.forward)
        target_in_location = world.component_for_entity(target, InLocation)
        # world.remove_component(target, InLocation)
        target_in_location.dungeon = None
        
        if user := world.try_component(ent_id, User):
            info = world.component_for_entity(ent_id, ActorInfo)
            target_info = world.component_for_entity(target, ActorInfo)
            user.mind.process_event("log", ("green", f"{info.name} catched {target_info.name}."))
            user.mind.process_event("redraw_ui")
            user.mind.process_event("player_acting_changed")
        for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
            if other_ent_id != ent_id and other_in_loc.dungeon == in_location.dungeon and in_location.position in other_sight.visible_tiles:
                other_user.mind.process_event("redraw_ui")
    