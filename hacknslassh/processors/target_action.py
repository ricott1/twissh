from __future__ import annotations
import esper
from hacknslassh.components.description import ActorInfo
from hacknslassh.components.item import ItemInfo
from hacknslassh.components.sight import Sight
from hacknslassh.components.user import User
from hacknslassh.components.acting import Acting
from hacknslassh.processors.action import Action

from ..components.in_location import InLocation
from hacknslassh.constants import *


class ToggleAutoTarget(Action):
    name = "target_toggle_auto"
    recoil_cost = Recoil.ZERO
    description = "Toggle auto target"

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        acting = world.try_component(ent_id, Acting)
        if not acting:
            return
        
        acting.auto_target = not acting.auto_target
        if user := world.try_component(ent_id, User):
            user.mind.process_event("acting_auto_target_updated", acting.target)
            user.mind.process_event("redraw_ui")


class Target(Action):
    name = "target"
    recoil_cost = Recoil.ZERO
    description = "Target"
    direction = 0

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        
        acting = world.try_component(ent_id, Acting)
        if not acting:
            return
        
        in_location = world.component_for_entity(ent_id, InLocation)
        sight: Sight = world.component_for_entity(ent_id, Sight)
        entities = []
        # entities will be sorted by distance because visible tiles is sorted by distance.
        for x, y in sight.visible_tiles:
            for z in (1, 0, 2): #first creatures layer, than items, than flyers
                # FIXME: within same layer, we should pick as "closest" the entity in the direction of ent_id
                if in_location.dungeon and (target_id := in_location.dungeon.get_at((x, y, z))):
                    if target_id == ent_id:
                        continue
                    if world.try_component(target_id, ActorInfo) or world.try_component(target_id, ItemInfo):
                        entities.append(target_id)
                
        if not entities:
            return
        
        if not acting.target or acting.target not in entities:
            acting.target = entities[0]
        else:
            acting.target = entities[(entities.index(acting.target) + cls.direction)%len(entities)]

        if user := world.try_component(ent_id, User):
            user.mind.process_event("acting_target_updated", acting.target)
            user.mind.process_event("redraw_ui")
    
class TargetNext(Target):
    name = "target_next"
    recoil_cost = Recoil.ZERO
    description = "Target next"
    direction = 1

class TargetPrevious(Target):
    name = "target_prev"
    recoil_cost = Recoil.ZERO
    description = "Target previous"
    direction = -1

class TargetSelf(Target):
    name = "target_self"
    recoil_cost = Recoil.ZERO
    description = "Target self"
    direction = 0

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        acting = world.try_component(ent_id, Acting)
        if not acting:
            return
        
        acting.target = ent_id
        if user := world.try_component(ent_id, User):
            user.mind.process_event("acting_target_updated", acting.target)
            user.mind.process_event("redraw_ui")