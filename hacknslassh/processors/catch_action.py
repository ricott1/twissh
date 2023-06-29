from __future__ import annotations
import esper
from hacknslassh.components.description import ActorInfo
from hacknslassh.components.sight import Sight
from hacknslassh.components.tokens import CatchableToken
from hacknslassh.components.user import User
from hacknslassh.components.acting import Acting
from hacknslassh.processors.action import Action
from hacknslassh.utils import distance

from ..components.in_location import InLocation
from hacknslassh.constants import *

class Catch(Action):
    name = "catch"
    recoil_cost = Recoil.LONG
    description = "Catch'm'all"
    range = Range.SHORT

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        
        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > 0:
            return
        
        target_id = acting.target
        if not target_id or not world.try_component(target_id, CatchableToken):
            return
        user = world.try_component(ent_id, User)
        target_in_location = world.component_for_entity(target_id, InLocation)
        target_info = world.component_for_entity(target_id, ActorInfo)
        in_location = world.component_for_entity(ent_id, InLocation)
        if distance(in_location.position, target_in_location.position) > cls.range:
            if user:
                user.mind.process_event("log", ("red", f"Can\'t pick up {target_info.name}: get closer!"))
            return

        acting.action_recoil = cls.recoil_cost
        #FIXME: add catch logic

        in_location.dungeon.remove_renderable_entity_at(target_in_location.position)
        target_in_location.dungeon = None
        acting.target = None

        if user:
            info = world.component_for_entity(ent_id, ActorInfo)
            user.mind.process_event("log", ("green", f"{info.name} catched {target_info.name}."))
            user.mind.process_event("redraw_ui")
            user.mind.process_event("player_acting_changed")
            user.mind.process_event("acting_target_updated", acting.target)
        for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
            if other_ent_id != ent_id and other_in_loc.dungeon == in_location.dungeon and in_location.position in other_sight.visible_tiles:
                other_user.mind.process_event("redraw_ui")
    